"""
entity abstract method for inheritence
"""


import abc

import mapping.maps
import pygame

class entity(abc.ABC):
    def __init__(self, posX, posY,hp, weapon, ai,spawnLoc, model):
        self.posX     = float(posX)
        self.posY     = float(posY)
        self.hp       = hp
        self.weapon   = weapon
        self.ai       = ai
        self.spawnLoc = spawnLoc
        self.model    = model


    @abc.abstractmethod
    def takeDamage(self):
        pass

    @abc.abstractmethod
    def inheritAI(self):
        pass

    @abc.abstractmethod
    def moveAndCollide(self, moveVec, roomId):
        wallRects = mapping.maps.getWallRects(roomId, self.screenW, self.screenH)


        self.posX += moveVec.x
        self.rect.x = int(self.posX)
        for wallRect in wallRects:
            if self.rect.colliderect(wallRect):
                if moveVec.x > 0:
                    self.rect.right = wallRect.left
                else:
                    self.rect.left = wallRect.right
                self.posX = float(self.rect.x)

        self.posY += moveVec.y
        self.rect.y = int(self.posY)
        for wallRect in wallRects:
            if self.rect.colliderect(wallRect):
                if moveVec.y > 0:
                    self.rect.bottom = wallRect.top
                else:
                    self.rect.top = wallRect.bottom
                self.posY = float(self.rect.y)

        self.rect.clamp_ip(pygame.Rect(0, 0, self.screenW, self.screenH))

        clampedX = float(self.rect.x)
        clampedY = float(self.rect.y)
        if clampedX != int(self.posX):
            self.posX = clampedX
        if clampedY != int(self.posY):
            self.posY = clampedY