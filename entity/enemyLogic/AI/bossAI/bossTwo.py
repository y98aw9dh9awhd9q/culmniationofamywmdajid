import pygame
import random
import math
import const

from entity.weapons.bullet import bullet
from mapping.maps import getWallRects, getBreakableRectsWithCoords, breakTile

class bossTwoAIClass:
    def __init__(self, enemy, screen, difficulty):
        self.enemy      = enemy
        self.screen     = screen
        self.difficulty = difficulty
        self.state      = "choose"
        self.last       = None
        self.bullets    = pygame.sprite.Group()
        self.data       = {}
        self.beamActive = False
        self.beamStart  = (0, 0)
        self.beamEnd    = (0, 0)
        self.phaseName  = "poo poo head"

    def update(self, deltaTime, roomId, player):
        self.player = player

        match self.state:
            case "choose"  : self.chooseAttack()
            case "spinner" : self.updateSpinner(deltaTime, roomId, player)
            case "burst"   : self.updateBurst(deltaTime, player)
            case "dash"    : self.updateDash(deltaTime, roomId, player)
            case "vtrap"   : self.updateVTrap(deltaTime, player)

        wallRects      = getWallRects(roomId, self.enemy.screenW, self.enemy.screenH)
        breakableData  = getBreakableRectsWithCoords(roomId, self.enemy.screenW, self.enemy.screenH)

        def onBreak(r, c):
            breakTile(roomId, r, c)

        self.bullets.update(
            deltaTime,
            self.enemy.screenW,
            self.enemy.screenH,
            wallRects      = wallRects,
            breakableData  = breakableData,
            onBreak        = onBreak
        )

    def chooseAttack(self):
        attacks = ["spinner", "burst", "dash", "vtrap"]

        if self.last:
            attacks = [a for a in attacks if a != self.last]
        self.state  = random.choice(attacks)
        self.last   = self.state

        match self.state:
            case "spinner" : self.startSpinner()
            case "burst"   : self.startBurst()
            case "dash"    : self.startDash()
            case "vtrap"   : self.startVTrap()

    def startSpinner(self):
        self.data = {
            "timer"    : 7,
            "cooldown" : 0,
            "offset"   : random.uniform(0, 360)
        }

    def updateSpinner(self, dt, roomId, player):
        self.data["timer"]      -= dt
        self.data["cooldown"]   -= dt
        ex, ey                   = self.enemy.rect.center
        px, py                   = player.rect.center
        move                     = pygame.Vector2(px - ex, py - ey)

        if move.length() > 0:
            move                 = move.normalize()

        self.enemy.moveAndCollide(move * 45 * dt, roomId)

        if self.data["cooldown"] <= 0:
            self.data["cooldown"] = random.uniform(0.1, 0.3)
            self.fireSpinner()

        if self.data["timer"]    <= 0:
            self.state            = "choose"

    def fireSpinner(self):
        ex, ey      = self.enemy.rect.center
        base_offset = self.data["offset"]

        for deg in range(0, 360, 45):

            ang = math.radians(deg + base_offset)
            tx  = ex + math.cos(ang) * 120
            ty  = ey + math.sin(ang) * 120

            self.bullets.add(
                bullet(
                    ex, ey,
                    tx, ty,
                    screen     = self.screen,
                    difficulty = 0.67 * self.difficulty,
                    owner      = "enemy",
                    damage     = self.enemy.atk,
                    color      = const.red
                )
            )

        self.data["offset"] = random.uniform(0, 360)

    def startBurst(self):
        self.data = {
            "bursts"   : 6,
            "shots"    : 5,
            "cooldown" : 0.25
        }

    def updateBurst(self, dt, player):
        self.data["cooldown"]        -= dt
        if self.data["cooldown"]     <= 0:
            self.fireBurst(player)
            self.data["shots"]       -= 1

            if self.data["shots"] > 0:
                self.data["cooldown"] = 0.06

            else:
                self.data["bursts"] -= 1

                if self.data["bursts"] <= 0:
                    self.state = "choose"
                    return

                self.data["shots"]    = 2
                self.data["cooldown"] = 1.5

    def fireBurst(self, player):

        ex, ey = self.enemy.rect.center
        px, py = player.rect.center

        base = pygame.Vector2(px - ex, py - ey).angle_to((1, 0))

        spread = [-45, -15, 0, 15, 45]

        for s in spread:

            ang = math.radians(-(base + s))

            tx = ex + math.cos(ang) * 120
            ty = ey + math.sin(ang) * 120

            self.bullets.add(
                bullet(
                    ex, ey,
                    tx, ty,
                    screen     = self.screen,
                    difficulty = 0.67 * self.difficulty,
                    owner      = "enemy",
                    damage     = self.enemy.atk,
                    color      = (0, 255, 255),
                    maxBounces = 1
                )
            )

    def startDash(self):
        ex, ey        = self.enemy.rect.center
        px, py        = self.player.rect.center
        direction     = pygame.Vector2(px - ex, py - ey)
        if direction.length() > 0:
            direction = direction.normalize()

        direction.rotate_ip(random.uniform(-20, 20))

        self.data = {
            "dir"       : direction,
            "dashCount" : 3
        }

    def updateDash(self, dt, roomId, player):
        speed = 750
        old   = pygame.Vector2(self.enemy.posX, self.enemy.posY)

        self.enemy.moveAndCollide(
            self.data["dir"] * speed * dt,
            roomId
        )

        moved = pygame.Vector2(
            self.enemy.posX - old.x,
            self.enemy.posY - old.y
        ).length()

        if moved < 3:
            self.data["dashCount"] -= 1
            if self.data["dashCount"] <= 0:
                self.state = "choose"
                return

            ex, ey = self.enemy.rect.center
            px, py = player.rect.center

            direction = pygame.Vector2(px - ex, py - ey)

            if direction.length() > 0:
                direction = direction.normalize()

            direction.rotate_ip(random.uniform(-20, 20))

            self.data["dir"] = direction

    def startVTrap(self):
        ex, ey = self.enemy.rect.center
        px, py = self.player.rect.center

        self.data = {
            "time"    : 7,
            "angle"   : math.atan2(py - ey, px - ex),
            "vCD"     : 0,
            "shotCD"  : 0
        }

        self.beamActive = False

    def updateVTrap(self, dt, player):
        ex, ey  = self.enemy.rect.center
        px, py  = player.rect.center
        target  = math.atan2(py - ey, px - ex)
        current = self.data["angle"]

        diff    = ((target - current + math.pi) % (2 * math.pi)) - math.pi

        self.data["angle"] += diff * dt * 0.8

        self.data["time"]   -= dt
        self.data["vCD"]    -= dt
        self.data["shotCD"] -= dt

        if self.data["vCD"] <= 0:
            self.data["vCD"] = 0.2
            self.fireV()

        if self.data["shotCD"] <= 0:
            self.data["shotCD"] = 0.65
            self.fireAtPlayer(player)

        if self.data["time"] <= 0:
            self.state = "choose"

    def fireV(self):
        ex, ey = self.enemy.rect.center
        spread = math.radians(25)

        for ang in (
            self.data["angle"] - spread,
            self.data["angle"] + spread
        ):

            tx = ex + math.cos(ang) * 120
            ty = ey + math.sin(ang) * 120

            self.bullets.add(
                bullet(
                    ex, ey,
                    tx, ty,
                    screen     = self.screen,
                    difficulty = 0.95 * self.difficulty,
                    owner      = "enemy",
                    damage     = self.enemy.atk,
                    color      = (255, 60, 60)
                )
            )

    def fireAtPlayer(self, player):

        ex, ey = self.enemy.rect.center
        px, py = player.rect.center

        self.bullets.add(
            bullet(
                ex, ey,
                px, py,
                screen     = self.screen,
                difficulty = 0.9 * self.difficulty,
                owner      = "enemy",
                damage     = self.enemy.atk,
                color      = (255, 220, 50)
            )
        )

    def draw(self, screen):
        self.bullets.draw(screen)
        if self.beamActive:

            ex, ey = self.enemy.rect.center
            bx, by = self.beamEnd

            surf   = pygame.Surface(
                (self.enemy.screenW, self.enemy.screenH),
                pygame.SRCALPHA
            )

            pygame.draw.line(
                surf,
                (255, 0, 0, 120),
                (ex, ey),
                (bx, by),
                10
            )

            screen.blit(surf, (0, 0))