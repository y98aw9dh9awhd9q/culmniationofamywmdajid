#ben nethaeyahoo and keyahhno acarkey
#2026-06-07
#dungeon crawller



import pygame
import mapping.mapGenerator as mapGenerator
import display
from player import player
from mapping.maps import getExitTiles

pygame.init()
screen             = pygame.display.set_mode((900, 600))
clock              = pygame.time.Clock()
font               = pygame.font.SysFont(None, 28)
winW, winH         = screen.get_size()
playerObj          = player(winW, winH)
mapGen             = mapGenerator.mapGenerator()
generatedMap       = None
currentRoomPosY    = 0
currentRoomPosX    = 0
transitionCooldown = 0.0

#exit dir index
mapDelta = {
    0: (-1,  0),
    1: ( 1,  0),
    2: ( 0, -1),
    3: ( 0,  1),
}

#what dir for new room
oppositeSide = {0: 1, 1: 0, 2: 3, 3: 2}

def getMatchingEntrance(roomID, comingFromDir, screenW, screenH, prevCenter):
    exits      = getExitTiles(roomID, screenW, screenH)
    targetDir  = oppositeSide[comingFromDir]
    candidates = [rect for rect, d in exits if d == targetDir]
    if not candidates:
        return None
    return min(candidates,
               key=lambda r:
               (r.centerx - prevCenter[0]) ** 2 +
               (r.centery - prevCenter[1]) ** 2)

def placePlayerAtDoor(playerObj, doorRect, comingFromDir):
    px, py = playerObj.rect.centerx, playerObj.rect.centery

    if comingFromDir == 0:
        playerObj.rect.centerx = px
        playerObj.rect.bottom  = doorRect.top - 1

    elif comingFromDir == 1:
        playerObj.rect.centerx = px
        playerObj.rect.top     = doorRect.bottom + 1

    elif comingFromDir == 2:
        playerObj.rect.centery = py
        playerObj.rect.right   = doorRect.left - 1

    elif comingFromDir == 3:
        playerObj.rect.centery = py
        playerObj.rect.left    = doorRect.right + 1


running = True
while running:
    deltaTime = clock.tick(60) / 1000.0
    events    = pygame.event.get()

    for event in events:
        if event.type == pygame.QUIT:
            running = False

    if not generatedMap:
        mapGen.setupMap()
        mapGen.generateMap()
        generatedMap = mapGen.printMap()

    if transitionCooldown > 0:
        transitionCooldown -= deltaTime

    currentRoomID = generatedMap[currentRoomPosY][currentRoomPosX]
    exitDir       = playerObj.touchingExit(currentRoomID)

    if exitDir is not None and transitionCooldown <= 0:
        prevCenter = playerObj.rect.center

        dy, dx = mapDelta[exitDir]
        newY   = currentRoomPosY + dy
        newX   = currentRoomPosX + dx

        #boundary guard
        mapH = len(generatedMap)
        mapW = len(generatedMap[0]) if mapH else 0
        if 0 <= newY < mapH and 0 <= newX < mapW:
            currentRoomPosY = newY
            currentRoomPosX = newX

            newRoomID = generatedMap[currentRoomPosY][currentRoomPosX]
            doorRect  = getMatchingEntrance(newRoomID, exitDir, winW, winH, prevCenter)

            if doorRect:
                placePlayerAtDoor(playerObj, doorRect, exitDir)

            transitionCooldown = 0.25 #prevent seizure or something idk

    screen.fill((0, 0, 0))
    display.drawRoom(screen, generatedMap[currentRoomPosY][currentRoomPosX])
    playerObj.update(deltaTime, generatedMap[currentRoomPosY][currentRoomPosX])
    display.drawPlayer(screen, playerObj)
    pygame.display.flip()

pygame.quit()