import pygame
import random
import math

import const
from entity.weapons.bullet import bullet
from mapping.maps import getWallRects, getBreakableRectsWithCoords, breakTile


class bossAIClass:
    """
    first boss ai!!!!!
    - shotgun phase
    - sniper phase
    - machine gun phase
    """

    shotgunCooldown = 0.35
    machineGunCoolDown = 0.02

    def __init__(self, enemy, screen, difficulty):
        self.enemy      = enemy
        self.screen     = screen
        self.difficulty = difficulty
        self.state      = "choose"
        self.bullets    = pygame.sprite.Group()
        self.data       = {}
        self.beamActive = False
        self.beamStart  = (0, 0)
        self.beamEnd    = (0, 0)
        self.beamAngle  = 0

    def update(self, deltaTime, roomId, player):
        self.player = player

        match self.state:
            case "choose"     : self.chooseAttack()
            case "shotgun"    : self.updateShotgun(deltaTime, roomId, player)
            case "sniper"     : self.updateSniper(deltaTime, roomId, player)
            case "machinegun" : self.updateMachinegun(deltaTime, roomId, player)

        wallRects = getWallRects(roomId, self.enemy.screenW, self.enemy.screenH)

        breakableData = getBreakableRectsWithCoords(
            roomId,
            self.enemy.screenW,
            self.enemy.screenH
        )

        def onBreak(r, c):
            breakTile(roomId, r, c)

        self.bullets.update(
            deltaTime,
            self.enemy.screenW,
            self.enemy.screenH,
            wallRects=wallRects,
            breakableData=breakableData,
            onBreak=onBreak
        )

    def chooseAttack(self):
        attacks = ["shotgun", "sniper", "machinegun"]

        if hasattr(self, "last"):
            attacks = [a for a in attacks if a != self.last]

        self.state = random.choice(attacks)
        self.last = self.state

        match self.state:
            case "shotgun"    : self.startShotgun()
            case "sniper"     : self.startSniper()
            case "machinegun" : self.startMachinegun()

    def startShotgun(self):
        self.data = {
            "dir"      : random.choice(  [-1,   1]),
            "shots"    : random.randint(8, 12),
            "cooldown" : 0.2
        }

    def updateShotgun(self, dt, roomId, player):
        ex, ey  = self.enemy.rect.center
        px, py  = player.rect.center
        toP     = pygame.Vector2(px - ex, py - ey)
        if toP.length() > 0:
            toP = toP.normalize()

        tangent = pygame.Vector2(-toP.y, toP.x) * self.data["dir"]
        old     = pygame.Vector2(self.enemy.posX, self.enemy.posY)
        self.enemy.moveAndCollide(tangent * 180 * dt, roomId)
        moved   = pygame.Vector2(self.enemy.posX - old.x, self.enemy.posY - old.y).length()

        if moved < 1:
            self.data["dir"]      *= -1
        self.data["cooldown"]     -= dt

        if self.data["cooldown"]  <= 0:
            self.data["cooldown"]  = self.shotgunCooldown
            self.data["shots"]    -= 1
            self.fireShotgun(player)

        if self.data["shots"]     <= 0:
            self.state = "choose"

    def fireShotgun(self, player):
        ex, ey    = self.enemy.rect.center
        px, py    = player.rect.center
        baseAngle = pygame.Vector2(px - ex, py - ey).angle_to((1, 0))
        spread    = [-25, -12, 0, 12, 25]

        for s in spread:
            ang = math.radians(-(baseAngle + s))
            tx  = ex + math.cos(ang) * 100
            ty  = ey + math.sin(ang) * 100

            self.bullets.add(bullet(
                    ex,       ey,
                    tx,       ty,
                    size      =(8, 8),
                    color     =(255, 80, 80),
                    damage    =self.enemy.atk,
                    owner     ="enemy",
                    screen    =self.screen,
                    difficulty=0.5*self.difficulty
                )
            )

    #sniper phase (telegraph - lock - shoot)
    def startSniper(self):
        self.data = {
            "phase"     : "reposition",
            "timer"     : 0,
            "beamAngle" : 0
        }

        self.beamActive = False

    def updateSniper(self, dt, roomId, player):
        ex, ey            = self.enemy.rect.center
        px, py            = player.rect.center
        d                 = self.data

        if d["phase"]    == "reposition":
            direction     = pygame.Vector2(ex - px, ey - py)

            if direction.length() > 0:
                direction = direction.normalize()

            target        = pygame.Vector2(px, py) + direction * 420
            move          = target                 - pygame.Vector2(ex, ey)

            if move.length() > 10:
                self.enemy.moveAndCollide(move.normalize() * 220 * dt, roomId)
            else:
                d["phase"] = "aim"
                d["timer"] = 1.5/self.difficulty

        elif d["phase"]   == "aim":
            d["timer"]    -= dt

            d["beamAngle"] = math.atan2(py - ey, px - ex)

            self.beamActive= True
            self.beamStart = (ex, ey)
            self.beamEnd   = (
                ex + math.cos(d["beamAngle"]) * 3000,
                ey + math.sin(d["beamAngle"]) * 3000
            )

            if d["timer"] <= 0:
                d["phase"] = "hold"
                d["timer"] = 0.2/self.difficulty

        elif d["phase"]   == "hold":
            d["timer"]    -= dt

            self.beamActive= True
            ex, ey         = self.enemy.rect.center

            angle          = d["beamAngle"]
            self.beamStart = (ex, ey)
            self.beamEnd   = (
                ex + math.cos(angle) * 3000,
                ey + math.sin(angle) * 3000
            )

            if d["timer"] <= 0:
                d["phase"] = "fire"
                d["timer"] = 0.35/self.difficulty

        elif d["phase"]   == "fire":
            d["timer"]    -= dt

            self.beamActive= True
            ex, ey         = self.enemy.rect.center
            angle          = d["beamAngle"]
            self.beamStart = (ex, ey)
            self.beamEnd   = (
                ex + math.cos(angle) * 3000,
                ey + math.sin(angle) * 3000
            )

            if d["timer"] <= 0:
                self.beamActive = False
                self.state = "choose"


    def fireSniper(self):
        self.beamActive = True
        ex, ey          = self.enemy.rect.center
        angle           = self.data["beamAngle"]
        self.beamStart  = (ex, ey)
        self.beamEnd    = (
            ex + math.cos(angle) * 3000,
            ey + math.sin(angle) * 3000
        )

    def beamHitsPlayer(self, player):
        if self.state != "sniper":
            return False

        if self.data.get("phase") != "fire":
            return False

        if not self.beamActive:
            return False

        px, py  = player.rect.center
        ax, ay  = self.beamStart
        bx, by  = self.beamEnd

        line    = pygame.Vector2(bx - ax, by - ay)
        point   = pygame.Vector2(px - ax, py - ay)

        if line.length_squared() == 0:
            return False

        t = max(0, min(1, point.dot(line) / line.length_squared()))
        closest = pygame.Vector2(ax, ay) + line * t

        dist = pygame.Vector2(px, py).distance_to(closest)

        print("beam dist:", dist)

        return dist < 18


    def startMachinegun(self):
        self.data = {
            "shots": 150,
            "cooldown": 0,
            "dir": pygame.Vector2(
                random.uniform(-1, 1),
                random.uniform(-1, 1)
            ).normalize()
        }

    def updateMachinegun(self, dt, roomId, player):
        ex, ey  = self.enemy.rect.center
        px, py  = player.rect.center
        d       = self.data
        toP     = pygame.Vector2(px - ex, py - ey)

        if toP.length() > 0:
            toP = toP.normalize()

        strafe  = pygame.Vector2(-toP.y, toP.x)
        move    = (strafe + d["dir"] * 0.3)

        if move.length() > 0:
            move= move.normalize()

        self.enemy.moveAndCollide(move * 160 * dt, roomId)

        d["cooldown"]    -= dt
        if d["cooldown"] <= 0:
            d["cooldown"] = self.machineGunCoolDown
            d["shots"]   -= 1
            self.fireMachinegun(player)

        if d["shots"] <= 0:
            self.state = "choose"

    def fireMachinegun(self, player):
        ex, ey = self.enemy.rect.center
        px, py = player.rect.center
        px    += random.randint(-45, 45)
        py    += random.randint(-45, 45)

        self.bullets.add(bullet(
                ex, ey,
                px, py,
                size      =(6, 6),
                color     =(255, 200, 60),
                damage    =self.enemy.atk,
                owner     ="enemy",
                screen    =self.screen,
                difficulty=0.8*self.difficulty
            )
        )

    def draw(self, screen):
        self.bullets.draw(screen)
        if self.beamActive:

            ex, ey    = self.enemy.rect.center
            bx, by    = self.beamEnd
            width     = self.enemy.screenW
            height    = self.enemy.screenH
            beam_surf = pygame.Surface((width, height), pygame.SRCALPHA)

            pygame.draw.line(
                beam_surf,
                (255, 0, 0, 120),
                (ex, ey),
                (bx, by),
                9
            )

            if self.data.get("phase") == "fire":
                pygame.draw.line(
                    beam_surf,
                    const.bulletRed,
                    (ex, ey),
                    (bx, by),
                    18
                )

            screen.blit(beam_surf, (0, 0))