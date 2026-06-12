import pygame
import math
import random
import const

class bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, targetX, targetY, screen, difficulty, crossingTime=0.7, size=(10, 10),
                 color=(255, 220, 50), damage=1, owner=None, maxBounces=0, ignoreWalls=False):
        super().__init__()
        self.damage = damage
        self.owner = owner
        self.maxBounces = maxBounces
        self.bouncesRemaining = maxBounces
        self.ignoreWalls = ignoreWalls

        scaledSize = const.scaleSize(size, screen[0], screen[1])
        self.image = pygame.Surface(scaledSize, pygame.SRCALPHA)
        self.image.fill(color)
        self.rect = self.image.get_rect(center=(x, y))
        self.posX = float(x)
        self.posY = float(y)
        self.screen = screen

        direction = pygame.Vector2(targetX - x, targetY - y)
        if direction.length() > 0:
            direction = direction.normalize()
        self.velocity = direction * (crossingTime * screen[0])
        if owner != "player":
            if isinstance(difficulty, str):
                difficulty = const.difficultyStats[difficulty]["bulletSpeed"]
            self.velocity *= difficulty

    def update(self, deltaTime, screenW, screenH, wallRects=None, breakableData=None, onBreak=None):
        self.posX += self.velocity.x * deltaTime
        self.posY += self.velocity.y * deltaTime
        self.rect.center = (self.posX, self.posY)

        if (self.rect.right < 0 or self.rect.left > screenW or
                self.rect.bottom < 0 or self.rect.top > screenH):
            self.kill()
            return

        if breakableData:
            for rect, rowIdx, colIdx in breakableData:
                if self.rect.colliderect(rect):
                    if onBreak:
                        onBreak(rowIdx, colIdx)
                    self.kill()
                    return

        if wallRects and not getattr(self, 'ignoreWalls', False):
            for wallRect in wallRects:
                if self.rect.colliderect(wallRect):
                    if self.bouncesRemaining <= 0:
                        self.kill()
                        return

                    overlapLeft = self.rect.right - wallRect.left
                    overlapRight = wallRect.right - self.rect.left
                    overlapTop = self.rect.bottom - wallRect.top
                    overlapBottom = wallRect.bottom - self.rect.top

                    minOverlap = min(
                        overlapLeft,
                        overlapRight,
                        overlapTop,
                        overlapBottom
                    )

                    speed = self.velocity.length()

                    angleOffset = math.radians(random.uniform(-45, 45))

                    if minOverlap in (overlapLeft, overlapRight):
                        baseAngle = 0 if self.velocity.x < 0 else math.pi
                    else:
                        baseAngle = math.pi / 2 if self.velocity.y < 0 else -math.pi / 2

                    newAngle = baseAngle + angleOffset

                    self.velocity.x = math.cos(newAngle) * speed
                    self.velocity.y = math.sin(newAngle) * speed

                    self.bouncesRemaining -= 1