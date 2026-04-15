from dataclasses import dataclass

import pygame

import const


@dataclass(frozen=True)
class room:
    # 0 = air
    # 1 = wall
    # 2 = breakable
    # 3 = exit
    # 4 = chest
    # 5 = shop
    # 6 = elevator
    layout: list
    # 0 = regular room
    # 1 = shop
    # 2 = boss room
    # 3 = exit
    type: int = 0

roomVariantOne = room([
    [1,1,1,1,1,1,3,3,3,1,1,1,1,1,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [3,0,0,0,0,0,0,0,0,0,0,0,0,0,3],
    [3,0,0,0,0,0,0,0,0,0,0,0,0,0,3],
    [3,0,0,0,0,0,0,0,0,0,0,0,0,0,3],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,1,1,1,1,1,3,3,3,1,1,1,1,1,1],
])

rooms = {1:roomVariantOne}


blockSize = 20

def drawMap(variant: int, screen):
    layout                     = rooms[variant].layout
    rows                       = len(layout)
    cols                       = len(layout[0])
    windowWidth, window_height = screen.get_size()
    blockWidth                 = windowWidth   / cols
    blockHeight                = window_height / rows

    for y, row in enumerate(layout):
        for x, val in enumerate(row):
            rect = pygame.Rect(
                x * blockWidth,
                y * blockHeight,
                blockWidth,
                blockHeight
            )

            if val == 1:
                pygame.draw.rect(screen, const.white, rect)
            if val == 2:
                pygame.draw.rect(screen, const.brown, rect)
            if val == 3 :
                pygame.draw.rect(screen, const.red, rect)
            pygame.draw.rect(screen, const.black, rect, 1)


    pygame.display.flip()


