import pygame
import sys
import maps

running = True

defaultSize = (800,600)
frameRate = 60

screen = pygame.display.set_mode(defaultSize,pygame.RESIZABLE)
clock = pygame.time.Clock()
fullScreen = False

pygame.init()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.VIDEORESIZE:
            screen = pygame.display.set_mode((event.w,event.h),pygame.RESIZABLE)
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_F11:
            fullScreen = not fullScreen
            if not fullScreen:
                screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            else:
                screen = pygame.display.set_mode(defaultSize,pygame.RESIZABLE)

    maps.drawMap(1,screen)


    clock.tick(frameRate)
    print(clock)
    pygame.display.flip()


pygame.quit()
sys.exit()