import random
import asyncio
import threading
from concurrent.futures import ThreadPoolExecutor
from collections import deque
from mapping.maps import roomRegistery
import numpy

directions  = ((-1, 0), (1, 0), (0, -1), (0, 1))
oppositeDir = (1, 0, 3, 2)

roomWeights = {
    0: 8,
    1: 1,
    5: 12,
    6: 18
}

counterKeys = {
    1: "shop",
    5: "chest",
    6: "doubleChest"
}

byExactExits = {}

for rid, robj in roomRegistery.items():

    if rid in (-1, -2, -3):
        continue

    byExactExits.setdefault(robj.exits, []).append(rid)

patternCache     = {}
patternCacheLock = threading.Lock()

def getLayer(r, c):
    return r + c

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

def buildWeightedPool(candidates, counters, limits):
    remaining = {
        "shop": limits["shop"] - counters["shop"],
        "chest": limits["chest"] - counters["chest"],
        "doubleChest": limits["doubleChest"] - counters["doubleChest"]
    }
    pool = []
    for rid in candidates:
        ck = counterKeys.get(roomRegistery[rid].type)
        if ck and counters[ck] >= limits[ck]:
            continue
        pool.extend([rid] * roomWeights.get(roomRegistery[rid].type, 1))
        if ck == "chest" and remaining["chest"] > 0:
            pool.extend([rid] * 3)

        if ck == "doubleChest" and remaining["doubleChest"] > 0:
            pool.extend([rid] * 5)
    return pool

#spanning tree========================================
def buildSpanningTree(size, prePlaced, rng, stopEvent):
    if stopEvent.is_set():
        return set()

    requiredExits = set()
    inTree        = set()
    frontier      = []

    for (pr, pc), pid in prePlaced.items():
        inTree.add((pr, pc))
        for d in range(4):
            if not roomRegistery[pid].exits[d]:
                continue

            dr, dc = directions[d]
            nr, nc = pr + dr, pc + dc

            if 0 <= nr < size and 0 <= nc < size and (nr, nc) not in inTree:
                frontier.append((nr, nc, pr, pc, d))

    if not frontier:
        for d in range(4):
            dr, dc = directions[d]
            if 0 <= dr < size and 0 <= dc < size:
                frontier.append((dr, dc, 0, 0, d))
                break

    allCells = size * size

    while frontier and len(inTree) < allCells:
        if stopEvent.is_set():
            return set()
        idx                         = rng.randrange(len(frontier))
        nr, nc, fromR, fromC, fromD = frontier[idx]
        frontier.pop(idx)
        if (nr, nc) in inTree:
            continue
        inTree.add((nr, nc))
        requiredExits.add((fromR, fromC, fromD))
        requiredExits.add((nr, nc, oppositeDir[fromD]))

        for d in range(4):
            dr, dc   = directions[d]
            nnr, nnc = nr + dr, nc + dc
            if 0 <= nnr < size and 0 <= nnc < size and (nnr, nnc) not in inTree:
                frontier.append((nnr, nnc, nr, nc, d))

    #remove conflicting tree edges
    for (pr, pc), pid in prePlaced.items():
        if stopEvent.is_set():
            return set()

        for d in range(4):
            if (pr, pc, d) not in requiredExits:
                continue

            if roomRegistery[pid].exits[d]:
                continue

            dr, dc = directions[d]
            nr, nc = pr + dr, pc + dc

            requiredExits.discard((pr, pc, d))
            requiredExits.discard((nr, nc, oppositeDir[d]))

            for d2 in range(4):
                dr2, dc2 = directions[d2]
                nr2, nc2 = nr + dr2, nc + dc2

                if 0 <= nr2 < size and 0 <= nc2 < size and (nr2, nc2) != (pr, pc):
                    requiredExits.add((nr, nc, d2))
                    requiredExits.add((nr2, nc2, oppositeDir[d2]))
                    break

    return requiredExits

#connectivity checks============================
def isFullyConnected(g, size):
    visited = set()
    queue   = deque([(0, 0)])
    visited.add((0, 0))

    while queue:
        r, c = queue.popleft()
        for d in range(4):
            dr, dc = directions[d]
            nr, nc = r + dr, c + dc
            if (nr, nc) in visited or not (0 <= nr < size and 0 <= nc < size):
                continue

            if roomRegistery[g[r * size + c]].exits[d] and roomRegistery[g[nr * size + nc]].exits[oppositeDir[d]]:
                visited.add((nr, nc))
                queue.append((nr, nc))

    return len(visited) == size * size

def isCompletable(g, size):
    if not isFullyConnected(g, size):
        return False

    exitPos = (size - 1, size - 1)
    visited = set()
    queue   = deque([(0, 0)])

    visited.add((0, 0))

    while queue:
        r, c = queue.popleft()
        if (r, c) == exitPos:
            return True

        for d in range(4):
            dr, dc = directions[d]
            nr, nc = r + dr, c + dc

            if (nr, nc) in visited or not (0 <= nr < size and 0 <= nc < size):
                continue

            if roomRegistery[g[r * size + c]].exits[d] and roomRegistery[g[nr * size + nc]].exits[oppositeDir[d]]:
                visited.add((nr, nc))
                queue.append((nr, nc))
    return False

#attempts
def runAttempt(size, bossPos, maxShop, maxChest, maxDoubleChest, seed, stopEvent):
    if stopEvent.is_set():
        return False, None

    rng       = random.Random(seed)
    g         = [0] * (size * size)
    g[0]      = -1
    g[-1]     = -2
    prePlaced = {
        (0, 0): -1,
        (size - 1, size - 1): -2
    }

    if bossPos:
        by, bx = bossPos
        g[by * size + bx] = -3
        prePlaced[(by, bx)] = -3

    requiredExits = buildSpanningTree(size, prePlaced, rng, stopEvent)

    if stopEvent.is_set():
        return False, None

    counters = {
        "shop"        : 0,
        "chest"       : 0,
        "doubleChest" : 0
    }

    limits = {
        "shop"        : maxShop,
        "chest"       : maxChest,
        "doubleChest" : maxDoubleChest
    }

    order = [(r, c) for r in range(size) for c in range(size) if g[r * size + c] == 0]
    layerSpecial = {}

    rngLocal = rng

    maxLayer = (size - 1) * 2

    for layer in range(maxLayer + 1):
        if rngLocal.random() < 0.75:
            layerSpecial[layer] = "left"
        else:
            layerSpecial[layer] = "top"

    layerRemaining = {}

    for layer, typ in layerSpecial.items():
        count = sum(1 for (r, c) in order if getLayer(r, c) == layer)
        layerRemaining[layer] = count

    def fillCell(idx):
        progress    = idx / len(order)
        chestTarget = progress * limits["chest"]

        if stopEvent.is_set():
            return False

        if idx == len(order):
            return isCompletable(g, size)

        r, c       = order[idx]
        pos        = r * size + c
        pat        = [None, None, None, None]
        conflict   = False

        for d in range(4):
            dr, dc = directions[d]
            nr, nc = r + dr, c + dc

            if not (0 <= nr < size and 0 <= nc < size):
                pat[d] = False
                continue

            treeReq     = True if (r, c, d) in requiredExits else None

            nb          = g[nr * size + nc]
            neighborReq = roomRegistery[nb].exits[oppositeDir[d]] if nb != 0 else None

            reqs = [x for x in (treeReq, neighborReq) if x is not None]

            if len(set(reqs)) > 1:
                conflict = True
                break

            pat[d] = reqs[0] if reqs else None

        if conflict:
            return False

        candidates       = candidatesForPattern(tuple(pat))
        remainingCells   = len(order) - idx
        validSpotsLeft   = remainingCells
        forcedCandidates = []

        if typ == "top" and -4 in candidates:
            forcedCandidates = [-4]

        elif typ == "left":
            leftOptions = [rid for rid in (-5, -6) if rid in candidates]

            if leftOptions:
                weighted = []
                for rid in leftOptions:
                    if rid == -5:
                        weighted.extend([rid] * 3)  # 75%
                    else:
                        weighted.append(rid)  # 25%
                forcedCandidates = weighted

        mustForce = False

        if typ == "top":
            mustForce = (-4 in candidates and validSpotsLeft == 1)

        elif typ == "left":
            mustForce = (
                    typ == "left"
                    and counters["chest"] < limits["chest"]
                    and len(candidates) <= 3
                    and validSpotsLeft <= 3
            )

        if mustForce:
            pool = forcedCandidates
        else:
            pool = buildWeightedPool(candidates, counters, limits)

            if forcedCandidates:
                pool.extend(forcedCandidates * 2)

        if not pool:
            return False

        rng.shuffle(pool)

        for rid in pool:
            if stopEvent.is_set():
                return False

            g[pos] = rid

            ck = counterKeys.get(roomRegistery[rid].type)
            if ck:
                counters[ck] += 1

            if fillCell(idx + 1):
                return True

            g[pos] = 0

            if ck:
                counters[ck] -= 1
        if counters["chest"] < chestTarget:
            forcedCandidates.extend([-5, -5, -5, -6])

        return False

    ok = fillCell(0)

    if stopEvent.is_set():
        return False, None

    grid = [g[row * size : (row + 1) * size] for row in range(size)]

    return ok, grid


#main map gen
class mapGenerator:
    def __init__(self):
        self.sizeLim          = 9
        self.size             = 3
        self.map              = None
        self.maxShop          = 1
        self.maxDoubleChest   = 1
        self.maxChest         = 1
        self.threadPool       = ThreadPoolExecutor(
            max_workers       =5,
            thread_name_prefix="mapGen"
        )
        self.stopEvent        = threading.Event()
        self.genTask          = None
        self.generating       = False
        self.progress         = 0.0
        self.result           = None

    #setup==============================
    def setupMap(self, boss=False):
        print("map gen: setupMap called")

        self.map = [[0] * self.size for _ in range(self.size)]
        self.map[0][0] = -1
        self.map[self.size - 1][self.size - 1] = -2

        if boss:
            self.map[self.size - 1][self.size - 2] = -3


    #start
    def startGenerateMap(self):
        if self.generating:
            return

        if self.threadPool is None:
            self.threadPool       = ThreadPoolExecutor(
                max_workers       =5,
                thread_name_prefix="mapGen"
            )

        self.genTask = asyncio.create_task(
            self.prGenerateMap()
        )

        print("map gen: async generation started")

    #async gen
    async def prGenerateMap(self):
        try:
            self.generating = True
            self.progress   = 0.0
            self.stopEvent.clear()

            loop = asyncio.get_running_loop()

            print("map gen: starting generation task")

            bossPos = None

            if self.map[self.size - 1][self.size - 2]== -3:
                bossPos = (
                    self.size - 1,
                    self.size - 2
                )

            baseSeed = random.randint(0, 10_000_000)
            tasks = []
            total = 3

            #launch attempts=============================
            for i in range(total):
                seed = baseSeed + i
                tasks.append(
                    loop.run_in_executor(
                        self.threadPool,
                        runAttempt,
                        self.size,
                        bossPos,
                        self.maxShop,
                        self.maxChest,
                        self.maxDoubleChest,
                        seed,
                        self.stopEvent
                    )
                )

            winnerGrid = None
            completed  = 0

            #collect results
            for coro in asyncio.as_completed(tasks):
                if self.stopEvent.is_set():
                    break

                try:
                    ok, grid = await coro
                except asyncio.CancelledError:
                    raise
                except Exception as e:

                    print("map gen: worker failed:", e)
                    continue

                completed += 1
                self.progress = completed / total
                print(f"map gen progress: {self.progress * 100:.1f}%")

                if ok and winnerGrid is None:
                    winnerGrid = grid
                    print("map gen: valid map found stopping others")

                    self.stopEvent.set()
                    break
            #finalize
            if winnerGrid is not None:
                self.map = winnerGrid
                self.result = winnerGrid
                print("map gen: sucess!!")
            else:
                print("map gen: failed all att")
                if self.map:
                    for r in range(self.size):
                        for c in range(self.size):
                            if self.map[r][c] == 0:
                                self.map[r][c] = -10

                self.result = self.map
            self.progress = 1.0
            return self.result
        except asyncio.CancelledError:
            print("map gen: async task cancelled")
            self.stopEvent.set()
            raise
        finally:
            self.generating = False

    def printMap(self):
        print(numpy.array(self.map))
        return self.map

    #final shutdown ====================
    def shutdown(self):
        print("map gen: shutdown started")
        self.generating = False
        self.progress   = 0.0
        self.stopEvent.set()
        try:
            if self.genTask:
                self.genTask.cancel()
        except Exception as e:
            print("map gen shutdown task cancel:", e)

        try:
            if self.threadPool:
                self.threadPool.shutdown(
                    wait=True,
                    cancel_futures=True
                )

        except Exception as e:
            print("map gen shutdown pool:", e)

        self.genTask    = None
        self.result     = None
        self.map        = None
        self.threadPool = None