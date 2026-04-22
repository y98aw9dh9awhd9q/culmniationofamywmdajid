import pygame
import const
import mapping.mapGenerator as mapGenerator
import display
from player import player
from mapping.maps import tileColors

pygame.init()
screen              = pygame.display.set_mode((900, 600))
clock               = pygame.time.Clock()
font                = pygame.font.SysFont(None, 28)
winW, winH          = screen.get_size()
playerObj           = player(winW, winH)
pendingRoomIndex    = None
mapGen = mapGenerator.mapGenerator()
generatedMap = None

currentRoomPosY = 0
currentRoomPosX = 0

#main loop
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

    """            if rowIdx == 0:
                direction = 0 #top
            elif rowIdx == rowCount - 1:
                direction = 1 #bottom
            elif colIdx == 0:
                direction = 2 #;eft
            elif colIdx == colCount - 1:
                direction = 3 #right
            exits.append((rect, direction))"""
    roomID = generatedMap[currentRoomPosY][currentRoomPosX]
    if playerObj.touchingExit(roomID):
        print(playerObj.rect.center)
        layout, rowCount, colCount, blockW, blockH = display.spaceCalculator(screen, roomID)
        for rowIdx, rowData in enumerate(layout):
            for colIdx, tileVal in enumerate(rowData):
                tileRect = pygame.Rect(colIdx * blockW, rowIdx * blockH, blockW, blockH)
                colorName = tileColors.get(tileVal)
                if colorName == "orange":
                    print(tileRect)
        try:
            match playerObj.touchingExit(roomID):
                case 0:
                    currentRoomPosY += 1
                    playerObj.rect.center = (playerObj.rect.centerx,playerObj.rect.centery-50)
                case 1:
                    currentRoomPosY -= 1
                    playerObj.rect.center = (playerObj.rect.centerx, playerObj.rect.centery +50)
                case 2:

                    currentRoomPosX -= 1
                    playerObj.rect.center = (blockW*2, playerObj.rect.centery)
                case 3:
                    currentRoomPosX += 1
                    playerObj.rect.center = (display.spaceCalculator(screen, roomID)[3]*2, playerObj.rect.centery )
        except:
            print("Index Error")

    screen.fill((0, 0, 0))

    display.drawRoom(screen, generatedMap[currentRoomPosY][currentRoomPosX])
    playerObj.update(deltaTime,generatedMap[currentRoomPosY][currentRoomPosX])
    display.drawPlayer(screen, playerObj)
    pygame.display.flip()


pygame.quit()

