import random
import threading #this was so FREAKING slow so its multithreaded now
from concurrent.futures import ThreadPoolExecutor, as_completed
from mapping.maps import roomRegistery
import numpy #formatting

#const
directions  = ((-1, 0), (1, 0), (0, -1), (0, 1))
oppositeDir = (1, 0, 3, 2)
roomWeights = {0: 10, 1: 1, 5: 4, 6: 2}
counterKeys = {1: "shop", 5: "chest", 6: "doubleChest"}

#id the rooms
byExactExits = {}
for rid, robj in roomRegistery.items():
    if rid <= 0:
        continue
    byExactExits.setdefault(robj.exits, []).append(rid)

#maps tuple of (T/F/None) of matching room ids
#None means dont care so the neighbors are not placed or dir is oob
patternCache     = {}
patternCacheLock = threading.Lock()

#return a tuple of all normal rood ids whose exits satisfy a 4 tuple where each element is T F or none
#cahces result after first call for each unique pattern
def candidatesForPattern(pattern):
    cached = patternCache.get(pattern)
    if cached is not None:
        return cached

    matches = []
    for exits, roomIds in byExactExits.items():
        if all(p is None or exits[d] == p for d, p in enumerate(pattern)):
            matches.extend(roomIds)

    result = tuple(matches)
    with patternCacheLock:
        patternCache[pattern] = result
    return result

#creates weighted pool of room
def buildWeightedPool(candidates, counters, limits):
    pool = []
    for rid in candidates:
        ck = counterKeys.get(roomRegistery[rid].type)
        if ck and counters[ck] >= limits[ck]:
            continue
        pool.extend([rid] * roomWeights.get(roomRegistery[rid].type, 1))
    return pool

#attempts to fill entire X by X grid uses rng seed so parallel attempts dont inferfere
#returns true, grid on succ or (False, partial) on fail
def runAttempt(size, bossPos, maxShop, maxChest, maxDoubleChest, seed):
    rng                   = random.Random(seed)
    g                     = [0] * (size * size)
    g[0]                  = -1                              # entrance (0, 0)
    g[-1]                 = -2                              # exit     (size-1, size-1)
    if bossPos:
        by, bx            = bossPos
        g[by * size + bx] = -3

    counters = {"shop": 0, "chest": 0, "doubleChest": 0}
    limits   = {"shop": maxShop, "chest": maxChest, "doubleChest": maxDoubleChest}

    #fill the cells in reading order ignoring the preplaced ones
    order = [(r, c) for r in range(size) for c in range(size) if g[r * size + c] == 0]

    def fillCell(idx):
        if idx == len(order):
            return True

        r, c = order[idx]

        #get required exits from placed exits
        pat = [None, None, None, None]
        for d in range(4):
            dr, dc   = directions[d]
            nr, nc   = r + dr, c + dc
            inBounds = 0 <= nr < size and 0 <= nc < size

            # cannot exit off grid
            if not inBounds:
                pat[d] = False
                continue

            #ignore if neighbour not placed
            neighborId = g[nr * size + nc]
            if neighborId == 0:
                continue

            #ensure exits are kissing
            pat[d] = roomRegistery[neighborId].exits[oppositeDir[d]]

        candidates = candidatesForPattern(tuple(pat))
        pool       = buildWeightedPool(candidates, counters, limits)
        if not pool:
            return False

        rng.shuffle(pool)

        for rid in pool:
            g[r * size + c] = rid
            ck = counterKeys.get(roomRegistery[rid].type)
            if ck:
                counters[ck] += 1

            if fillCell(idx + 1):
                return True

            g[r * size + c] = 0
            if ck:
                counters[ck] -= 1

        return False

    ok   = fillCell(0)
    grid = [g[row * size : (row + 1) * size] for row in range(size)]
    return ok, grid

#finally the meat and potatoes
class MapGenerator:
    def __init__(self):
        self.sizeLim        = 9
        self.size           = 3
        self.map            = None
        self.maxShop        = 1
        self.maxDoubleChest = 1
        self.maxChest       = 1
        self.threadPool     = ThreadPoolExecutor(max_workers=67, thread_name_prefix="mapGen")

    #init
    def setupMap(self, boss=False):
        self.map                                   = [[0] * self.size for _ in range(self.size)]
        self.map[0][0]                             = -1
        self.map[self.size - 1][self.size - 1]     = -2
        if boss:
            self.map[self.size - 1][self.size - 2] = -3

    def increaseMapSize(self):
        if self.size < self.sizeLim:
            self.size += 1

    #starts 67 parallel attempts on first success stores and executes failiures
    def generateMap(self):
        bossPos = None
        if self.map[self.size - 1][self.size - 2] == -3:
            bossPos = (self.size - 1, self.size - 2)

        baseSeed = random.randint(0, 10000000) #seed to ensure no interferance

        futureToIdx = {
            self.threadPool.submit(
                runAttempt,
                self.size,
                bossPos,
                self.maxShop,
                self.maxChest,
                self.maxDoubleChest,
                baseSeed + i,
            ): i
            for i in range(5)
        }

        winnerGrid = None

        for future in as_completed(futureToIdx): #required snake case because python named it that
            try:
                ok, grid = future.result()
                #fire name ik
            except Exception:
                print(f"exception caught skipping")
                continue

            if ok and winnerGrid is None:
                winnerGrid = grid
                for otherFuture in futureToIdx:
                    if otherFuture is not future:
                        otherFuture.cancel()

        if winnerGrid is not None:
            self.map = winnerGrid
            print(f"successfully generated map")
        else:
            print("failed all att ")
            for r in range(self.size):
                for c in range(self.size):
                    if self.map[r][c] == 0:
                        self.map[r][c] = -10

        self.printMap()

    def printMap(self):
        print(numpy.array(self.map))
        return self.map

    def shutdown(self):
        self.threadPool.shutdown(wait=False)


#testing purpose
import time
mapGen = MapGenerator()
for i in range(10):
    mapGen.increaseMapSize()
    mapGen.setupMap(boss=(i % 2 == 1))
    t = time.perf_counter()
    mapGen.generateMap()
    print(f"{(time.perf_counter() - t) * 1000:.1f} ms\n") #used to take 1000000 years
mapGen.shutdown()