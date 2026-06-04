import pygame
import math
import random

class bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, targetX, targetY, screen, difficulty, crossingTime= 0.7, size=(10, 10),
                 color=(255, 220, 50), damage=1, owner=None, maxBounces=0 ):
        super().__init__()
        self.damage           = damage
        self.owner            = owner #hit filtering purpose
        self.maxBounces       = maxBounces
        self.bouncesRemaining = maxBounces

        self.image            = pygame.Surface(size, pygame.SRCALPHA)
        self.image.fill(color)
        self.rect             = self.image.get_rect(center=(x, y))
        self.posX             = float(x)
        self.posY             = float(y)
        self.screen           = screen

        direction = pygame.Vector2(targetX - x, targetY - y)
        if direction.length() > 0:
            direction = direction.normalize()
        self.velocity = direction * (crossingTime*screen[0])
        if owner != "player":
            self.velocity*=difficulty



        #print(self.velocity)

    def update(self, deltaTime, screenW, screenH, wallRects=None, breakableData=None, onBreak=None):
        self.posX += self.velocity.x * deltaTime
        self.posY += self.velocity.y * deltaTime
        self.rect.center = (self.posX, self.posY)

        if (self.rect.right < 0 or self.rect.left > screenW or
                self.rect.bottom < 0 or self.rect.top > screenH):
            self.kill()
            return

        #ensure breakables get checked and intercepts if walltiles = {1,2}
        if breakableData:
            for rect, rowIdx, colIdx in breakableData:
                if self.rect.colliderect(rect):
                    if onBreak:
                        onBreak(rowIdx, colIdx)
                    self.kill()
                    return

        if wallRects:
            for wallRect in wallRects:
                if self.rect.colliderect(wallRect):

                    if self.bouncesRemaining <= 0:
                        self.kill()
                        return

                    overlapLeft     = self.rect.right - wallRect.left
                    overlapRight    = wallRect.right - self.rect.left
                    overlapTop      = self.rect.bottom - wallRect.top
                    overlapBottom   = wallRect.bottom - self.rect.top

                    minOverlap      = min(
                        overlapLeft,
                        overlapRight,
                        overlapTop,
                        overlapBottom
                    )

                    speed           = self.velocity.length()

                    angleOffset     = math.radians(random.uniform(-45, 45))

                    if minOverlap in (overlapLeft, overlapRight):
                        baseAngle   = 0 if self.velocity.x < 0 else math.pi

                    else:
                        baseAngle   = math.pi / 2 if self.velocity.y < 0 else -math.pi / 2

                    newAngle        = baseAngle + angleOffset

                    self.velocity.x = math.cos(newAngle) * speed
                    self.velocity.y = math.sin(newAngle) * speed

                    self.bouncesRemaining -= 1