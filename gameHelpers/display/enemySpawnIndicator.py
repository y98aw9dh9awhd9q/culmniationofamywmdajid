import pygame
import const
from entity.entityClass import enemyBuilder
from entity.enemyLogic.reader.enemySheetReader import getRandomEnemy

class enemySpawnIndicator:
    def __init__(self, row, col, blockW, blockH, layerID, screenW, screenH, screen):
        self.centerX     = int(col * blockW + (blockW / 2))
        self.centerY     = int(row * blockH + (blockH / 2))
        self.maxRadius   = int(min(blockW, blockH) / 2)
        self.radius      = 0
        self.expandSpeed = 2
        self.shrinkSpeed = 2
        self.holdFrames  = 5
        self.holdCounter = 0
        self.state       = "growing"
        self.done        = False
        self.layerID     = layerID
        self.screenW     = screenW
        self.screenH     = screenH
        self.spawnPos    = (int(col * blockW), int(row * blockH))
        self.enemy       = None   # set once at hold state
        self.spawned     = False
        self.blockH      = blockH
        self.blockW      = blockW
        self.screen      = screen

    def update(self):
        match self.state:
            case "growing":
                self.radius += self.expandSpeed
                if self.radius >= self.maxRadius:
                    self.radius = self.maxRadius
                    self.state  = "holding"

            case "holding":
                if not self.spawned:
                    self.enemy = enemyBuilder(
                        enemyName = getRandomEnemy(self.layerID),
                        spawnPos  = self.spawnPos,
                        layer     = self.layerID,
                        screenW   = self.screenW,
                        screenH   = self.screenH,
                        gridH     = self.blockH,
                        gridW     = self.blockW,
                    )
                    self.spawned = True

                self.holdCounter += 1
                if self.holdCounter >= self.holdFrames:
                    self.state = "shrinking"

            case "shrinking":
                self.radius -= self.shrinkSpeed
                if self.radius <= 0:
                    self.radius = 0
                    self.done   = True

    def draw(self, screen):
        if self.radius > 0:
            pygame.draw.circle(
                screen,
                const.enemySpawnIndicatorColor,
                (self.centerX, self.centerY),
                int(self.radius),
                0
            )