import pygame
import random

from entity.weapons.bullet import bullet
from mapping.maps import getWallRects, getBreakableRectsWithCoords, breakTile


class machineGunnerAIClass:
    shootCooldown = 0.02

    def __init__(self, enemy, screen, difficulty):
        self.enemy      = enemy
        self.screen     = screen
        self.difficulty = difficulty
        self.bullets    = pygame.sprite.Group()
        self.cooldown   = 0
        self.shots      = 35
        self.reload     = 0
        self.dir        = pygame.Vector2(
            random.uniform(-1, 1),
            random.uniform(-1, 1)
        )
        if self.dir.length() > 0:
            self.dir    = self.dir.normalize()

    def update(self, dt, roomId, player):
        self.updateMovement(dt, roomId, player)
        self.updateShooting(dt, player)

        wallRects     = getWallRects(roomId, self.enemy.screenW, self.enemy.screenH)
        breakableData = getBreakableRectsWithCoords(roomId, self.enemy.screenW, self.enemy.screenH)

        self.bullets.update(
            dt,
            self.enemy.screenW,
            self.enemy.screenH,
            wallRects     = wallRects,
            breakableData = breakableData,
            onBreak       = lambda r, c: breakTile(roomId, r, c) #oh my god so tuff
        )

    def updateMovement(self, dt, roomId, player):
        ex, ey   = self.enemy.rect.center
        px, py   = player.rect.center

        toP      = pygame.Vector2(px - ex, py - ey)
        if toP.length() > 0:
            toP  = toP.normalize()

        strafe   = pygame.Vector2(-toP.y, toP.x)
        move     = (strafe + self.dir * 0.3)
        if move.length() > 0:
            move = move.normalize()

        self.enemy.moveAndCollide(move * 140 * dt, roomId)

    def updateShooting(self, dt, player):
        if self.shots      <= 0:
            self.reload    -= dt
            if self.reload <= 0:
                self.shots  = 50
            return

        self.cooldown   -= dt
        if self.cooldown > 0:
            return

        self.cooldown = self.shootCooldown
        self.shots   -= 1
        self.fire(player)

    def fire(self, player):
        ex, ey = self.enemy.rect.center
        px, py = player.rect.center
        px    += random.randint(-25, 25)
        py    += random.randint(-25, 25)

        self.bullets.add(bullet(
            ex, ey,
            px, py,
            size=(6, 6),
            color=(255, 200, 60),
            damage=self.enemy.atk,
            owner="enemy",
            screen=self.screen,
            difficulty=0.8 * self.difficulty
        ))