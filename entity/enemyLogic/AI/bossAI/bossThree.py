import pygame
import math
import random
import const
from entity.weapons.bullet import bullet
from mapping.maps import getWallRects




class orbitShield:
    def __init__(self, angle):
        self.angle  = angle
        self.radius = 120
        self.hp     = 60












class bossThreeAIClass:
    def __init__(self, enemy, screen, difficulty):
        self.enemy      = enemy
        self.screen     = screen
        self.difficulty = difficulty
        self.state      = "telegraph"
        self.last       = None
        self.phase      = 1
        self.maxHp      = enemy.hp
        self.bullets    = pygame.sprite.Group()
        self.shields    = []
        self.beamAngle  = 0
        self.beamSpeed  = 0.8
        self.beamLength = max(enemy.screenW, enemy.screenH) * 2
        self.beamLines  = []
        self.shotCount  = 0

        self.data = {
            "telegraphTimer": 0.0,
            "stateTimer":     0.0,
        }

        self.enemy.moveAndCollide = self.lockedMove


    def lockedMove(self, moveVec, roomId):
        return


    def update(self, dt, roomId, player):
        self.player    = player
        if self.phase == 1 and self.enemy.hp <= self.maxHp * 0.5:
            self.startPhaseTwo()

        match self.state:
            case "telegraph"   : self.updateTelegraph(dt)
            case "spinner"     : self.updateSpinner(dt, player)
            case "beamSpinner" : self.updateBeamSpinner(dt, player)
            case "meatballs"   : self.updateMeatballs(dt, player)

        wallRects = getWallRects(roomId, self.enemy.screenW, self.enemy.screenH)

        self.bullets.update(
            dt,
            self.enemy.screenW,
            self.enemy.screenH,
            wallRects=wallRects
        )

        if self.phase == 2:
            self.updateShields(dt)


    def startPhaseTwo(self):
        self.phase              = 2
        self.shields            = []
        self.beamSpeed          = 0.55
        self.state              = "beamSpinner"
        self.shotCount          = 0
        self.data["stateTimer"] = 0.0

        for i in range(5):
            self.shields.append(orbitShield(math.radians(i * 72)))

    def updateTelegraph(self, dt):
        ex, ey = self.enemy.rect.center

        self.data["telegraphTimer"] = self.data.get("telegraphTimer", 0.0) + dt

        self.beamLines = self.buildBeamLines(ex, ey)

        if self.data["telegraphTimer"] >= 1.0:
            self.data["telegraphTimer"] = 0.0
            self.data["stateTimer"]     = 0.0
            self.state = "beamSpinner"

    def buildBeamLines(self, ex, ey):
        lines = []
        for i in range(6):
            ang        = self.beamAngle + (2 * math.pi / 6) * i
            bx         = ex + math.cos(ang) * self.beamLength
            by         = ey + math.sin(ang) * self.beamLength
            lines.append(((ex, ey), (bx, by)))
        if self.phase == 2:
            slowAngle  = -self.beamAngle * 0.55
            for i in range(3):
                ang    = slowAngle + (2 * math.pi / 3) * i
                bx     = ex + math.cos(ang) * self.beamLength
                by     = ey + math.sin(ang) * self.beamLength
                lines.append(((ex, ey), (bx, by)))
        return lines

    def updateBeamGeometry(self, dt):
        ex, ey          = self.enemy.rect.center
        self.beamAngle += self.beamSpeed * dt
        self.beamLines  = self.buildBeamLines(ex, ey)

    def updateSpinner(self, dt, player):
        ex, ey         = self.enemy.rect.center
        px, py         = player.rect.center

        if self.phase == 2:
            self.updateBeamGeometry(dt)

        self.data["shotCD"]     = self.data.get("shotCD", 0.0) - dt
        if self.data["shotCD"] <= 0:
            self.data["shotCD"] = 0.35 if self.phase == 1 else 0.3

            self.bullets.add(
                bullet(ex, ey, px, py, self.screen,
                       difficulty=0.6 * self.difficulty,
                       owner="enemy",
                       damage=self.enemy.atk,
                       color=const.cyan)
            )

        self.data["ringCD"] = self.data.get("ringCD", 0.0) - dt
        if self.data["ringCD"] <= 0:
            self.data["ringCD"] = 1.35 if self.phase == 1 else 1.1

            baseOffset = random.uniform(0, 360)
            for deg in range(0, 360, 60):
                ang = math.radians(deg + baseOffset)
                tx  = ex + math.cos(ang) * 140
                ty  = ey + math.sin(ang) * 140

                self.bullets.add(
                    bullet(ex, ey, tx, ty, self.screen,
                           difficulty=0.75 * self.difficulty,
                           owner="enemy",
                           damage=self.enemy.atk,
                           color=const.blue)
                )

        self.data["stateTimer"] = self.data.get("stateTimer", 0.0) + dt
        if self.data["stateTimer"] > 6.5:
            self.data["stateTimer"] = 0.0
            self.state = "beamSpinner"

    def updateBeamSpinner(self, dt, player):
        ex, ey = self.enemy.rect.center
        px, py = player.rect.center

        self.updateBeamGeometry(dt)

        self.data["beamShot"]     = self.data.get("beamShot", 0.0) - dt
        if self.data["beamShot"] <= 0:
            self.data["beamShot"] = 0.42 if self.phase == 1 else 0.32

            count = 1 if self.phase == 1 else 2

            for _ in range(count):
                offset   = random.uniform(-22, 22)
                ang      = math.atan2(py - ey, px - ex) + math.radians(offset)
                tx       = ex + math.cos(ang) * 200
                ty       = ey + math.sin(ang) * 200

                isBouncy = (self.phase == 2) and (self.shotCount % 2 == 1)
                self.shotCount += 1

                self.bullets.add(
                    bullet(ex, ey, tx, ty, self.screen,
                           difficulty=0.85 * self.difficulty,
                           owner="enemy",
                           damage=self.enemy.atk,
                           color=const.purple if isBouncy else const.red,
                           maxBounces=3 if isBouncy else 0)
                )

        self.data["stateTimer"] = self.data.get("stateTimer", 0.0) + dt
        if self.data["stateTimer"] > 7.2:
            self.data["stateTimer"] = 0.0
            self.state = "meatballs"

    def updateMeatballs(self, dt, player):
        ex, ey         = self.enemy.rect.center
        px, py         = player.rect.center

        if self.phase == 2:
            self.updateBeamGeometry(dt)

        self.data["mbCD"]     = self.data.get("mbCD", 0.0) - dt
        if self.data["mbCD"] <= 0:
            self.data["mbCD"] = 1.8 if self.phase == 1 else 1.45

            self.bullets.add(
                bullet(ex, ey, px, py, self.screen,
                       difficulty =0.45 * self.difficulty,
                       owner      ="enemy",
                       damage     =self.enemy.atk,
                       color      =const.orange,
                       maxBounces = 0,
                       size       =(26, 26))
            )

        self.data["fastCD"]     = self.data.get("fastCD", 0.0) - dt
        if self.data["fastCD"] <= 0:
            self.data["fastCD"] = 0.3 if self.phase == 1 else 0.25

            count = 2 if self.phase == 1 else 3
            for _ in range(count):
                offset = random.uniform(-28, 28)
                ang    = math.atan2(py - ey, px - ex) + math.radians(offset)
                tx     = ex + math.cos(ang) * 160
                ty     = ey + math.sin(ang) * 160

                self.bullets.add(
                    bullet(ex, ey, tx, ty, self.screen,
                           difficulty = 0.95 * self.difficulty,
                           owner      ="enemy",
                           damage     = self.enemy.atk,
                           color      = const.yellow)
                )

        self.data["stateTimer"]     = self.data.get("stateTimer", 0.0) + dt
        if self.data["stateTimer"]  > 6.0:
            self.data["stateTimer"] = 0.0
            self.state = "spinner"

    def updateShields(self, dt):
        ex, ey = self.enemy.rect.center

        for i, shield in enumerate(self.shields):
            shield.angle += dt * (2.2 if i % 2 == 0 else -1.6)
            shield.x      = ex + math.cos(shield.angle) * shield.radius
            shield.y      = ey + math.sin(shield.angle) * shield.radius

    def beamHitsPlayer(self, player):
        if not self.beamLines:
            return False

        px, py    = player.rect.center
        playerPos = pygame.Vector2(px, py)
        thickness = 16

        for a, b in self.beamLines:
            p1   = pygame.Vector2(a)
            p2   = pygame.Vector2(b)
            line = p2 - p1
            if line.length() == 0:
                continue

            #its there again, the projection factor
            t       = max(0, min(1, (playerPos - p1).dot(line) / line.length_squared()))
            closest = p1 + line * t

            if (closest - playerPos).length() < thickness:
                return True

        return False



    def shieldBlocksBullet(self, bulletSprite):
        if self.phase != 2:
            return False

        bx, by = bulletSprite.rect.center
        bpos   = pygame.Vector2(bx, by)

        for shield in self.shields:
            if not hasattr(shield, "x"):
                continue
            s = pygame.Vector2(shield.x, shield.y)
            if (s - bpos).length() < 30:
                shield.hp -= bulletSprite.damage
                if shield.hp <= 0:
                    self.shields.remove(shield)
                return True
        return False

    def draw(self, screen):
        self.bullets.draw(screen)

        if self.beamLines:
            isTelegraph = self.state == "telegraph"
            color       = (255, 220, 60, 60) if isTelegraph else (255, 60, 60)
            width       = 12 if isTelegraph else 18

            surf        = pygame.Surface((self.enemy.screenW, self.enemy.screenH), pygame.SRCALPHA)
            for a, b in self.beamLines:
                pygame.draw.line(surf, color, a, b, width)
            screen.blit(surf, (0, 0))

        if self.phase == 2:
            for shield in self.shields:
                if hasattr(shield, "x"):
                    pygame.draw.circle(screen, const.cyan, (int(shield.x), int(shield.y)), 28)