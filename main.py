#ben nethaeyahoo and keyahhno acarkey and emotional support horp
#2026-06-07
#dungeon crawller whjere you go through epstein stuff and then fight the scret boss
#the secret boss is emmanuel and he is the ultimate gooner


import pygame
import mapping.mapLogic.mapGenerator as mapGenerator
import display
import data.dataSaving
from entitity.player import player
from mapping.maps import getExitTiles
import mainMenu.subMenu.settings as settings
import mainMenu.menu as menu
import mapping.mapLogic.tutorialGen as tutorial

pygame.init()
screen             = pygame.display.set_mode((900, 600))
clock              = pygame.time.Clock()
font               = pygame.font.SysFont(None, 28)
cfg    = settings.loadSettings()
screen = settings.applySettings(cfg)
loadedSettings = settings.loadSettings()

def mainMenu():
    menuResult = menu.run(screen, clock, font)
    print(menuResult)
    if menuResult[0] == "quit":
        pygame.quit()
        raise SystemExit

mainMenu()




playerObj          = player(*screen.get_size())
mapGen             = mapGenerator.mapGenerator()
generatedMap       = False
currentRoomPosY    = 0
currentRoomPosX    = 0
transitionCooldown = 0.0

if loadedSettings["tutorial"]:
    print("start tutorial")
    currentLayerID     = [0,1]
else:
    currentLayerID     = [1, 0]
playerSavePrep         = None
print(currentLayerID)
#exit dir index
mapDelta = {
    0: (-1,  0),
    1: ( 1,  0),
    2: ( 0, -1),
    3: ( 0,  1),
}

#layer name
# 1  - epstein 's island
# 2  - epstein 's temple
# 3  - epstein 's dungeon
# 4  - epstein 's cellar
# 5  - epstein 's tunnel
# 6  - epstein 's upper layer
# 7  - epstein 's lower layer
# 8  - epstein 's vault
# 9  - epstein 's throne room
# 10 - Emmanuel's goon cave

#sprite classes
playerSpriteGroup = pygame.sprite.Group()
playerSpriteGroup.add(playerObj)

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


mapSize = 3
def generateMap():
    global mapSize, currentLayerID
    print(currentLayerID, "map gen called")
    if currentLayerID is None:
        currentLayerID = [1,1]



    if currentLayerID[1] == 5:
        mapSize += 1
        mapGen.increaseMapSize()
        currentLayerID[0] = currentLayerID[0] + 1
        currentLayerID[1] = 1
    if currentLayerID[1] == 4:
        mapGen.setupMap(boss=True)
        mapGen.generateMap()
        generatedMap = mapGen.printMap()
    else:
        mapGen.setupMap()
        mapGen.generateMap()
        generatedMap = mapGen.printMap()
    currentLayerID[1] = currentLayerID[1] + 1
    return generatedMap

#prestart data check
saveDataRead = data.dataSaving.readSave()
if saveDataRead:
    print(saveDataRead)
    generatedMap = saveDataRead[1]
    try:
        currentRoomPosX       = saveDataRead[0][1]
        currentRoomPosY       = saveDataRead[0][2]
        playerObj.rect.center = saveDataRead[0][-1]
    except:
        currentRoomPosX, currentRoomPosY = 0, 0
        playerObj.rect.center = screen.get_size()[0] / 2, screen.get_size()[1] / 2
    currentLayerID = saveDataRead[2]






running = True
while running:

    cfg               = settings.loadSettings()
    deltaTime         = clock.tick(cfg["fpsCap"]) / 1000.0
    events            = pygame.event.get()
    winW, winH        = screen.get_size()
    playerObj.screenW = winW
    playerObj.screenH = winH

    for event in events:
        if event.type == pygame.QUIT:
            try:
                saveDat = (playerSavePrep, generatedMap, currentLayerID)
                data.dataSaving.saveData(saveDat)
            except:
                print("save error")
            running = False

        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            mainMenu()



    if not generatedMap:
        print(currentLayerID)
        if currentLayerID[0] >= 1:
            generatedMap = generateMap()
        else:
            print("tutorialMap")
            generatedMap = tutorial.tutorialMatching[currentLayerID[1]]

    if transitionCooldown > 0:
        transitionCooldown -= deltaTime

    #print(generatedMap, currentRoomPosY, currentRoomPosX)
    currentRoomID = generatedMap[currentRoomPosY][currentRoomPosX]
    exitDir       = playerObj.touchingExit(currentRoomID)

    if playerObj.touchingElevator(currentRoomID):
        currentRoomID         = -1  #-1 is the entrance always
        currentRoomPosX       = 0
        currentRoomPosY       = 0
        if currentLayerID[0] >= 1:
            generatedMap      = generateMap()
        else:
            currentLayerID[1]+= 1
            generatedMap      = tutorial.tutorialMatching[currentLayerID[1]]

    if exitDir is not None and transitionCooldown <= 0:

        prevCenter = playerObj.rect.center
        dy, dx     = mapDelta[exitDir]
        newY       = currentRoomPosY + dy
        newX       = currentRoomPosX + dx

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

            transitionCooldown = 0.25                #prevent seizure or something idk
            playerSavePrep = (newRoomID,             #0 - room ID the player enters
                              currentRoomPosX,       #1 - posX of the room in the grid
                              currentRoomPosY,       #2 - posY of the room in the grid
                              playerObj.rect.center  # 3 - player rect
                              )
            print(currentLayerID)

    screen.fill((0, 0, 0))
    display.drawRoom(screen, generatedMap[currentRoomPosY][currentRoomPosX])
    playerObj.update(deltaTime, generatedMap[currentRoomPosY][currentRoomPosX])
    playerObj.bullets.draw(screen)  # draw all active player bullets
    display.drawPlayer(screen, playerObj)

    pygame.display.flip()

pygame.quit()