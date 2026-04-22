
#this might be the most bs code ever but whatever by power of nagra it shall work

import random
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from mapping.maps import roomRegistery
import numpy

directions  = ((-1, 0), (1, 0), (0, -1), (0, 1))
oppositeDir = (1, 0, 3, 2)
roomWeights = {0: 10, 1: 1, 5: 4, 6: 2}
counterKeys = {1: "shop", 5: "chest", 6: "doubleChest"}

byExactExits = {}
for rid, robj in roomRegistery.items():
    if rid <= 0:
        continue
    byExactExits.setdefault(robj.exits, []).append(rid)

patternCache     = {}
patternCacheLock = threading.Lock()

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
    pool = []
    for rid in candidates:
        ck = counterKeys.get(roomRegistery[rid].type)
        if ck and counters[ck] >= limits[ck]:
            continue
        pool.extend([rid] * roomWeights.get(roomRegistery[rid].type, 1))
    return pool

def buildSpanningTree(size, prePlaced, rng):
    #prims algo
    #makes a set of cells with different means to guarantee an open exit ( R, C, d)
    #d guarantees all cells are reachable from the entrance
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
        idx                          = rng.randrange(len(frontier))
        nr, nc, fromR, fromC, fromD  = frontier[idx]
        #this looks so weird  but in the name of boris we must do it
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

    #remove conflicting tree edges that conflict with a preplaced room
    #reattach orphaned cell via diff neighbor
    for (pr, pc), pid in prePlaced.items():
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
                dr2, dc2   = directions[d2]
                nr2, nc2   = nr + dr2, nc + dc2
                if 0 <= nr2 < size and 0 <= nc2 < size and (nr2, nc2) != (pr, pc):
                    requiredExits.add((nr, nc, d2))
                    requiredExits.add((nr2, nc2, oppositeDir[d2]))
                    break

    return requiredExits

def runAttempt(size, bossPos, maxShop, maxChest, maxDoubleChest, seed):
    rng   = random.Random(seed)
    g     = [0] * (size * size)
    g[0]  = -1
    g[-1] = -2
    prePlaced = {(0, 0): -1, (size - 1, size - 1): -2}
    if bossPos:
        by, bx              = bossPos
        g[by * size + bx]   = -3
        prePlaced[(by, bx)] = -3

    requiredExits = buildSpanningTree(size, prePlaced, rng)

    counters = {"shop": 0, "chest": 0, "doubleChest": 0}
    limits   = {"shop": maxShop, "chest": maxChest, "doubleChest": maxDoubleChest}

    order = [(r, c) for r in range(size) for c in range(size) if g[r * size + c] == 0]

    def fillCell(idx):
        if idx == len(order):
            return True

        r, c     = order[idx]
        pos      = r * size + c
        pat      = [None, None, None, None]
        conflict = False
        for d in range(4):
            dr, dc   = directions[d]
            nr, nc   = r + dr, c + dc
            inBounds = 0 <= nr < size and 0 <= nc < size

            if not inBounds:
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

        candidates = candidatesForPattern(tuple(pat))
        pool       = buildWeightedPool(candidates, counters, limits)
        if not pool:
            return False

        rng.shuffle(pool)
        for rid in pool:
            g[pos] = rid
            ck     = counterKeys.get(roomRegistery[rid].type)
            if ck:
                counters[ck] += 1

            if fillCell(idx + 1):
                return True

            g[pos] = 0
            if ck:
                counters[ck] -= 1

        return False

    ok   = fillCell(0)
    grid = [g[row * size : (row + 1) * size] for row in range(size)]
    return ok, grid


class mapGenerator:
    def __init__(self):
        self.sizeLim        = 9
        self.size           = 3
        self.map            = None
        self.maxShop        = 1
        self.maxDoubleChest = 1
        self.maxChest       = 1
        self.threadPool     = ThreadPoolExecutor(max_workers=5, thread_name_prefix="mapGen")

    def setupMap(self, boss=False):
        self.map                                   = [[0] * self.size for _ in range(self.size)]
        self.map[0][0]                             = -1
        self.map[self.size - 1][self.size - 1]     = -2
        if boss:
            self.map[self.size - 1][self.size - 2] = -3

    def increaseMapSize(self):
        if self.size < self.sizeLim:
            self.size += 1

    def generateMap(self):
        bossPos = None
        if self.map[self.size - 1][self.size - 2] == -3:
            bossPos = (self.size - 1, self.size - 2)

        baseSeed    = random.randint(0, 10_000_000)
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
        for future in as_completed(futureToIdx):
            try:
                ok, grid = future.result()
            except Exception:
                continue
            if ok and winnerGrid is None:
                winnerGrid = grid
                for otherFuture in futureToIdx:
                    if otherFuture is not future:
                        otherFuture.cancel()

        if winnerGrid is not None:
            self.map = winnerGrid
            print("successfully generated map")
        else:
            print("failed all attempts")
            for r in range(self.size):
                for c in range(self.size):
                    if self.map[r][c] == 0:
                        self.map[r][c] = -10

    def printMap(self):
        print(numpy.array(self.map))
        return self.map

    def shutdown(self):
        self.threadPool.shutdown(wait=False)