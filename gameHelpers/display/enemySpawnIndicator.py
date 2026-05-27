import pygame
import const

from gameHelpers.display.display import spaceCalculator
from mapping.maps import getEnemySpawns

spawnIndicators      = []
spawnEffectsStarted  = False

class enemySpawnIndicator:
    def __init__(self, row, col, blockW, blockH):
        self.centerX       = int(col * blockW + (blockW / 2))
        self.centerY       = int(row * blockH + (blockH / 2))
        self.maxRadius     = int(min(blockW, blockH) / 2)
        self.radius        = 0
        self.expandSpeed   = 2
        self.shrinkSpeed   = 2
        self.holdFrames    = 5
        self.holdCounter   = 0
        self.state         = "growing"
        self.done          = False

    def update(self):
        match self.state:
            case "growing":
                self.radius += self.expandSpeed
                if self.radius >= self.maxRadius:
                    self.radius = self.maxRadius
                    self.state  = "holding"

            case "holding":
                self.holdCounter += 1
                if self.holdCounter >= self.holdFrames:
                    self.state = "shrinking"

            case "shrinking":
                self.radius -= self.shrinkSpeed
                if self.radius <= 0:
                    self.radius = 0
                    self.done   = True

    def draw(self, screen):
        pygame.draw.circle(screen,
                           const.enemySpawnIndicatorColor,
                           (self.centerX, self.centerY),int(self.radius),0)

def resetSpawnEffects():
    global spawnIndicators
    global spawnEffectsStarted
    spawnIndicators.clear()
    spawnEffectsStarted = False

def drawSpawnEffects(screen, roomId, layerId, difficulty):
    global spawnEffectsStarted
    layout, rowCount, colCount, blockW, blockH = spaceCalculator(screen, roomId)

    if not spawnEffectsStarted:
        enemySpawns = getEnemySpawns(roomId,layerId,difficulty)
        for row, col in enemySpawns:
            spawnIndicators.append(enemySpawnIndicator(row,col,blockW,blockH))
        spawnEffectsStarted = True

    for indicator in spawnIndicators:
        indicator.update()
        indicator.draw(screen)

    spawnIndicators[:] = [indicator for indicator in spawnIndicators if not indicator.done]