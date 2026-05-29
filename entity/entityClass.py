import pygame
import mapping.maps

import entity.enemyLogic.reader.enemySheetReader as reader
import const

from entity.enemyLogic.AI.fodderAI import fodderAIClass
from entity.enemyLogic.AI.tripletAI import tripletAIClass

def aiMatcher(aiName, enemy,screen, difficulty):
    match aiName:
        case "fodder": return fodderAIClass(enemy, screen, difficulty)
        case "triplet":return tripletAIClass(enemy,screen, difficulty)
        case _ :return None


class enemyBuilder(pygame.sprite.Sprite):
    def __init__(self, enemyName, spawnPos, layer, screenW, screenH, gridH, gridW, difficulty):
        super().__init__()
        self.enemyName = enemyName
        self.hp        = int(reader.readLayers(layer)[enemyName]["hp"])
        self.atk       = int(reader.readLayers(layer)[enemyName]["atk"])
        self.weapon    = reader.readLayers(layer)[enemyName]["weapon"]
        self.screenW   = screenW
        self.screenH   = screenH
        self.posX      = float(spawnPos[0])
        self.posY      = float(spawnPos[1])
        imagePath      = const.enemyPths[enemyName]
        self.image     = pygame.image.load(imagePath).convert_alpha()
        self.image     = pygame.transform.scale(self.image, (gridW * 0.75, gridH * 0.75))
        self.rect      = self.image.get_rect(topleft=(int(self.posX), int(self.posY)))
        aiName         = reader.readLayers(layer)[enemyName]["ai"]
        self.ai        = aiMatcher(aiName, self, (self.screenW, self.screenH),difficulty)

    def update(self, roomId, player, deltaTime):
        if self.ai is not None:
            self.ai.update(deltaTime, roomId, player)

    def draw(self, screen):
        screen.blit(self.image, self.rect)
        if self.ai is not None and hasattr(self.ai, "bullets"):
            self.ai.bullets.draw(screen)

    def takeDamage(self, dmg):
        self.hp        -= dmg

    def isDead(self):
        return self.hp <= 0

    def moveAndCollide(self, moveVec, roomId):
        wallRects                                   = mapping.maps.getWallRects(roomId, self.screenW, self.screenH)

        self.posX                                  += moveVec.x
        self.rect.x                                 = int(self.posX)
        for wallRect in wallRects:
            if self.rect.colliderect(wallRect):
                if moveVec.x > 0:   self.rect.right = wallRect.left
                elif moveVec.x < 0: self.rect.left  = wallRect.right
                self.posX = float(self.rect.x)

        self.posY                                   += moveVec.y
        self.rect.y                                  = int(self.posY)
        for wallRect in wallRects:
            if self.rect.colliderect(wallRect):
                if moveVec.y > 0:   self.rect.bottom = wallRect.top
                elif moveVec.y < 0: self.rect.top    = wallRect.bottom
                self.posY = float(self.rect.y)

        self.rect.clamp_ip(pygame.Rect(0, 0, self.screenW, self.screenH))
        self.posX = float(self.rect.x)
        self.posY = float(self.rect.y)