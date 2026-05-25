import pygame
import math
import asyncio
import json
from gameHelpers.SHUTDOWN import fullShutdown
import const

cyan          = (0x74, 0xd9, 0xf7)
gridCol       = (180, 180, 180)
scaleOfCube   = 500

def rotX(v, a):
    x,y,z=v; c,s=math.cos(a),math.sin(a)
    return [x, y*c-z*s, y*s+z*c]

def rotY(v, a):
    x,y,z=v; c,s=math.cos(a),math.sin(a)
    return [x*c+z*s, y, -x*s+z*c]

def rotZ(v, a):
    x,y,z=v; c,s=math.cos(a),math.sin(a)
    return [x*c-y*s, x*s+y*c, z]

def project(v, cx, cy, scale=scaleOfCube):
    x,y,z = v
    z += 6
    f = scale / z
    return (cx + int(x*f), cy - int(y*f))


cubelet  = 2.0 / 3.0


cubeFaces = [
    #(name,normal,u-axis,v-axis,origin of 0,0 sticker)
    ("U",  ( 0, 1, 0), ( 1,0,0), ( 0,0,-1), (-1, 1, 1)),
    ("D",  ( 0,-1, 0), ( 1,0,0), ( 0,0, 1), (-1,-1,-1)),
    ("F",  ( 0, 0,-1), ( 1,0,0), ( 0,1, 0), (-1,-1,-1)),
    ("B",  ( 0, 0, 1), (-1,0,0), ( 0,1, 0), ( 1,-1, 1)),
    ("R",  ( 1, 0, 0), ( 0,0,-1), ( 0,1, 0), ( 1,-1, 1)),
    ("L",  (-1, 0, 0), ( 0,0, 1), ( 0,1, 0), (-1,-1,-1)),
]


def faceQuads(faceIdx):
    """
    returns 9 quads which is a list of 4 xyz corners for the given face
    they are ordered [row 0..2][col 0..2], row 0 = top, col 0 = left
    """
    name, normal, u, v, origin = cubeFaces[faceIdx]
    quads = []
    for row in range(3):
        for col in range(3):
            ox = origin[0] + u[0]*col*cubelet + v[0]*row*cubelet
            oy = origin[1] + u[1]*col*cubelet + v[1]*row*cubelet
            oz = origin[2] + u[2]*col*cubelet + v[2]*row*cubelet
            nx,ny,nz = normal
            ox += nx*0.01; oy += ny*0.01; oz += nz*0.01
            corners = [
                [ox,          oy,          oz],
                [ox+u[0]*cubelet, oy+u[1]*cubelet, oz+u[2]*cubelet],
                [ox+u[0]*cubelet+v[0]*cubelet,
                 oy+u[1]*cubelet+v[1]*cubelet,
                 oz+u[2]*cubelet+v[2]*cubelet],
                [ox+v[0]*cubelet, oy+v[1]*cubelet, oz+v[2]*cubelet],
            ]
            quads.append(corners)
    return quads





#rotation state

#orientation angles in degrees
globalRotX = 25.0    #tilt so the cube looks 3d
globalRotY = 20.0    #side angle
globalSpin = 0.0     #y spin added per frame
sliceAnim  = None
sliceQueue = []


def applyGlobal(v):
    r = rotX(v, math.radians(globalRotX))
    r = rotY(r, math.radians(globalRotY + globalSpin))
    return r


def applySliceOffset(corner, slicePhase):
    if slicePhase is None:
        return corner
    x,y,z = corner
    face  = slicePhase["face"]
    ang   = math.radians(slicePhase["angle"])
    if face == "L":
        if x < -0.32:
            return rotY(corner, ang)
    elif face == "R":
        if x > 0.32:
            return rotY(corner, -ang)
    elif face == "M":
        if -0.32 <= x <= 0.32:
            return rotY(corner, ang)
    return corner


def projectCorners(corners, cx, cy, slicePhase):
    pts = []
    for c in corners:
        r = applySliceOffset(c, slicePhase)
        r = applyGlobal(r)
        pts.append(project(r, cx, cy))
    return pts


def dotNormal(normal, slicePhase, cx, cy):
    c = [normal[0]*0.5, normal[1]*0.5, normal[2]*0.5]
    r = applySliceOffset(c, slicePhase)
    r = applyGlobal(r)
    return -r[2]


def drawRubiksCube(screen, progress, slicePhase):
    global globalSpin

    w, h  = screen.get_size()
    cx    = w // 2
    cy    = h // 2 - 50

    letterFont = pygame.font.SysFont(None, 36)

    showC   = progress >= 0.25
    showAmp = progress >= 0.50
    showA   = progress >= 0.75

    letterMap = {}
    if showC:   letterMap.update({(r,0):"C" for r in range(3)})
    if showAmp: letterMap.update({(r,1):"&" for r in range(3)})
    if showA:   letterMap.update({(r,2):"A" for r in range(3)})

    faceOrder = sorted(range(6), key=lambda fi: dotNormal(cubeFaces[fi][1], slicePhase, cx, cy))

    for fi in faceOrder:
        faceName = cubeFaces[fi][0]
        normal   = cubeFaces[fi][1]
        dot      = dotNormal(normal, slicePhase, cx, cy)
        if dot >= 0:
            continue

        quads = faceQuads(fi)
        shade = max(60, int(255 * min(1.0, abs(dot) * 1.2)))

        for idx, corners in enumerate(quads):
            row, col = divmod(idx, 3)
            pts = projectCorners(corners, cx, cy, slicePhase)

            fillCol = (shade, shade, shade)
            pygame.draw.polygon(screen, fillCol, pts)
            pygame.draw.polygon(screen, gridCol, pts, 1)

            if faceName == "F":
                letter = letterMap.get((row, col))
                if letter:
                    centroid = (sum(p[0] for p in pts)//4,
                                sum(p[1] for p in pts)//4)
                    col_ = cyan if letter in ("C","A") else const.white
                    surf = letterFont.render(letter, True, col_)
                    r    = surf.get_rect(center=centroid)
                    screen.blit(surf, r)

    if progress >= 0.75:
        globalSpin += 2.5 * (1 + (progress - 0.75) * 8)
    else:
        globalSpin += 0.4



def buildSliceQueue():
    """
    returns the sequence of slice moves to animate across the duration of the loading
    each entry: (triggerProgress, face, degrees)
    """
    return [
        (0.00, "L",  90),   #c appears at 25%
        (0.25, "M",  90),   #& appears at 50%
        (0.50, "R", -90),   #a appears at 75%
    ]



sliceState     = None
lastProgress   = 0.0
pendingMoves   = None
animAngle      = 0.0
animTarget     = 0.0
animFace       = None

def initAnim():
    global pendingMoves, sliceState, lastProgress, animAngle, animTarget, animFace
    pendingMoves = buildSliceQueue()
    sliceState   = None
    lastProgress = 0.0
    animAngle    = 0.0
    animTarget   = 0.0
    animFace     = None

initAnim()


def tickSlice(progress):
    global sliceState, animAngle, animTarget, animFace, pendingMoves

    #check if a new move should start
    if pendingMoves:
        trigger, face, deg = pendingMoves[0]
        if progress >= trigger:
            pendingMoves.pop(0)
            animFace   = face
            animAngle  = 0.0
            animTarget = deg

    #animates current slice
    if animFace is not None and abs(animAngle) < abs(animTarget):
        step = math.copysign(min(4.0, abs(animTarget - animAngle)), animTarget)
        animAngle += step
        sliceState = {"face": animFace, "angle": animAngle}
    elif animFace is not None:
        animAngle  = animTarget
        sliceState = {"face": animFace, "angle": animAngle}


def loadingBar(screen, font, progress, text="poo poo head"):
    screen.fill(const.black)

    tickSlice(progress)
    drawRubiksCube(screen, progress, sliceState)

    w, h      = screen.get_size()
    barWidth  = int(w * 0.6)
    barHeight = 34
    x         = (w - barWidth) // 2
    y         = h - barHeight - 24

    pygame.draw.rect(screen, (50,50,50), (x, y, barWidth, barHeight), border_radius=6)
    fillW = int(barWidth * max(0.0, min(1.0, progress)))
    if fillW > 0:
        pygame.draw.rect(screen, (0, 200, 0), (x, y, fillW, barHeight), border_radius=6)

    title   = font.render(text,                      True, const.white)
    percent = font.render(f"{int(progress*100)}%",   True, const.white)
    screen.blit(title,   (x, y - 46))
    screen.blit(percent, (x, y - 82))

    pygame.display.flip()

async def generateEntireWorld(mapGen, screen, font, worldCache):
    initAnim()   #reset the animation

    if not worldCache:
        worldCache = {}

    totalFloors = 9 * 4
    completed   = 0

    for layer in range(1, 10):
        worldCache[str(layer)] = {}

        for floor in range(1, 5):

            if layer == 1 and floor == 1:
                mapGen.size = 3
                mapGen.setupMap(boss=False)
                await mapGen.prGenerateMap()
                worldCache["1"]["1"] = mapGen.result
                completed += 1
                loadingBar(screen, font, completed / totalFloors, "generating: 1-1")
                continue

            floorText = f"generating: {layer}-{floor}"
            print(floorText)

            mapGen.size = min(3 + (layer - 1), 9)
            mapGen.setupMap(boss=(floor == 4))

            generationTask = asyncio.create_task(mapGen.prGenerateMap())

            while not generationTask.done():
                combinedProgress = (completed + mapGen.progress) / totalFloors
                loadingBar(screen, font, combinedProgress, floorText)
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        fullShutdown()
                await asyncio.sleep(0)

            generated = await generationTask
            mapGen.printMap()

            worldCache[str(layer)][str(floor)] = generated
            completed += 1

            saveStructure = {
                "playerData": {"savePrep": None, "weapon": ["pistol#1"], "layer": [1,1]},
                "worldData":  {"layers": worldCache},
                "metaData":   {"visitedRooms": [[0,0]]}
            }
            with open("data/gameSaveData/save.json","w") as f:
                json.dump(saveStructure, f, indent=4)
            print(f"saved to save {layer}-{floor}")

    holdFrames = 60 #except the agme doesnt run at 60fps locked
    for _ in range(holdFrames):
        loadingBar(screen, font, 1.0, "completed!")
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                fullShutdown(mapGen)
        await asyncio.sleep(1/60)

    print("mapGeneration: shutting down")
    mapGen.shutdown()