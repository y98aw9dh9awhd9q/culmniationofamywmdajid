import pygame
import const
import mapping.mapGenerator as mapGenerator
import display
from player import player

pygame.init()
screen              = pygame.display.set_mode((900, 600))
clock               = pygame.time.Clock()
font                = pygame.font.SysFont(None, 28)
winW, winH          = screen.get_size()
playerObj           = player(winW, winH)
pendingRoomIndex    = None
mapGen = mapGenerator.mapGenerator()
generatedMap = None

currentRoomX = 0
currentRoomY = 0

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
    if playerObj.touchingExit(generatedMap[currentRoomX][currentRoomY]):
        print(playerObj.touchingExit(generatedMap[currentRoomX][currentRoomY]))

    screen.fill((0, 0, 0))

    display.drawRoom(screen, generatedMap[currentRoomX][currentRoomY])
    playerObj.update(deltaTime,generatedMap[currentRoomX][currentRoomY])
    display.drawPlayer(screen, playerObj)
    pygame.display.flip()


pygame.quit()

