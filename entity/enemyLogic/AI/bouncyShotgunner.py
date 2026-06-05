import pygame
import random
import math

import const
from entity.weapons.bullet import bullet
from mapping.maps import getWallRects, getBreakableRectsWithCoords, breakTile


class bouncyShotgunnerAIClass:
    shootCooldown = 2
    moveInterval = 1.0
    moveSpeed = 90

    def __init__(self, enemy, screen, difficulty):
        self.enemy      = enemy
        self.screen     = screen
        self.difficulty = difficulty
        self.bullets    = pygame.sprite.Group()
        self.shootTimer = random.uniform(0, self.shootCooldown)
        self.moveTimer  = 0.0
        self.targetX    = enemy.posX
        self.targetY    = enemy.posY
        self.dir        = random.choice([-1, 1])

    def update(self, dt, roomId, player):
        self.shootTimer -= dt
        self.moveTimer  -= dt

        self.handleShooting(player)
        self.handleMovement(dt, roomId)

        wallRects     = getWallRects(roomId, self.enemy.screenW, self.enemy.screenH)
        breakableData = getBreakableRectsWithCoords(roomId, self.enemy.screenW, self.enemy.screenH)

        self.bullets.update(
            dt,
            self.enemy.screenW,
            self.enemy.screenH,
            wallRects=wallRects,
            breakableData=breakableData,
            onBreak=lambda r, c: breakTile(roomId, r, c)
        )

    def handleShooting(self, player):
        if self.shootTimer > 0:
            return

        self.shootTimer    = self.shootCooldown
        self.pickNewMoveTarget(player)
        self.fire(player)

    def handleMovement(self, dt, roomId):
        dx   = self.targetX - self.enemy.posX
        dy   = self.targetY - self.enemy.posY
        dist = (dx * dx + dy * dy) ** 0.5

        if dist > 3:
            move = pygame.Vector2(dx, dy).normalize() * self.moveSpeed * dt
            self.enemy.moveAndCollide(move, roomId)

    def pickNewMoveTarget(self, player):
        px, py       = player.rect.center
        angle        = random.uniform(0, math.tau)
        radius       = random.randint(120, 220)
        self.targetX = px + math.cos(angle) * radius
        self.targetY = py + math.sin(angle) * radius

    def fire(self, player):
        ex, ey       = self.enemy.rect.center
        px, py       = player.rect.center
        baseAngle    = pygame.Vector2(px - ex, py - ey).angle_to((1, 0))
        spread       = [-50, 0, 50]

        for s in spread:
            ang = math.radians(-(baseAngle + s))
            tx  = ex + math.cos(ang) * 100
            ty  = ey + math.sin(ang) * 100

            self.bullets.add(bullet(
                ex, ey,
                tx, ty,
                size       = (10, 10),
                color      = const.blue,
                damage     = self.enemy.atk,
                owner      = "enemy",
                screen     = self.screen,
                difficulty = 0.6 * self.difficulty,
                maxBounces = 5
            ))