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
p                   = player(winW, winH)
pendingRoomIndex    = None
mapGen = mapGenerator.mapGenerator()
generatedMap = None

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

    display.drawRoom(screen, generatedMap[1][1])
    pygame.display.update()


pygame.quit()

