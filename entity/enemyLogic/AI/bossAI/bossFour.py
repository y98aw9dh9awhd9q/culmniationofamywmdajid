import math
import random
import pygame
import const
from entity.weapons.bullet import bullet
from mapping.maps import getWallRects, getBreakableRectsWithCoords, breakTile

class delayedAimBullet(bullet):
    def __init__(self, x, y, targetX, targetY, screen, difficulty, delay, **kwargs):
        super().__init__(x, y, targetX, targetY, screen, difficulty, **kwargs)
        self.velocity          = pygame.Vector2(0, 0)
        self.delay             = delay
        self.aim               = (targetX, targetY)
        self.savedDifficulty   = difficulty
        self.savedCrossingTime = kwargs.get("crossingTime", 0.7)

    def update(self, deltaTime, screenW, screenH, wallRects=None, breakableData=None, onBreak=None):
        if self.delay > 0:
            self.delay -= deltaTime
            if self.delay <= 0:
                target = pygame.Vector2(self.aim)
                direction = target - pygame.Vector2(self.rect.center)
                if direction.length() > 0:
                    self.velocity = direction.normalize() * (self.savedCrossingTime * self.screen[0]) * self.savedDifficulty
            return

        super().update(deltaTime, screenW, screenH, wallRects, breakableData, onBreak)

class explodingBullet(bullet):
    def __init__(self, *args, childCount=18, childColor=(255, 160, 40), **kwargs):
        super().__init__(*args, **kwargs)
        self.childCount = childCount
        self.childColor = childColor

    def explode(self, group):
        x, y      = self.rect.center
        for i in range(self.childCount):
            angle = math.tau * i / self.childCount
            group.add(
                bullet(
                    x, y,
                    x + math.cos(angle) * 160,
                    y + math.sin(angle) * 160,
                    screen       = self.screen,
                    difficulty   = 0.9,
                    crossingTime = 0.55,
                    size         = (7, 7),
                    color        = self.childColor,
                    damage       = self.damage,
                    owner        = "enemy",
                )
            )
        self.kill()

class triangleShot(pygame.sprite.Sprite):
    def __init__(self, x, y, angle, speed, damage, screen, shootsEyes=False, target=None):
        super().__init__()
        self.image = pygame.Surface((74, 64), pygame.SRCALPHA)
        pts        = [(37, 2), (4, 60), (70, 60)]
        pygame.draw.polygon(self.image, (255, 210, 40), pts, 3)
        pygame.draw.polygon(self.image, (255, 210, 40, 45), pts)
        self.image      = pygame.transform.rotate(self.image, -math.degrees(angle) + 90)
        self.rect       = self.image.get_rect(center=(x, y))
        self.pos        = pygame.Vector2(x, y)
        self.velocity   = pygame.Vector2(math.cos(angle), math.sin(angle)) * speed
        self.damage     = damage
        self.owner      = "enemy"
        self.screen     = screen
        self.shootsEyes = shootsEyes
        self.target     = target
        self.eyeTimer   = 0.55

    def update(self, deltaTime, screenW, screenH, wallRects=None, breakableData=None, onBreak=None):
        self.pos += self.velocity * deltaTime
        self.rect.center = self.pos
        self.eyeTimer -= deltaTime
        if self.rect.right < 0 or self.rect.left > screenW or self.rect.bottom < 0 or self.rect.top > screenH:
            self.kill()
            return

        if wallRects:
            for wallRect in wallRects:
                if self.rect.colliderect(wallRect):
                    self.kill()
                    return

class bossFourAIClass:
    def __init__(self, enemy, screen, difficulty):
        self.enemy               = enemy
        self.screen              = screen
        self.difficulty          = difficulty
        self.maxHp               = enemy.hp
        self.phase               = 1
        self.state               = None
        self.queue               = []
        self.data                = {}
        self.bullets             = pygame.sprite.Group()
        self.warnPoints          = []
        self.lasers              = []
        self.sniperBeam          = None
        self.sniperBeamActive    = False
        self.moveTarget          = pygame.Vector2(enemy.rect.center)
        self.moveTimer           = 0
        self.desperation         = False
        self.desperationDuration = 30.0
        self.desperationTimer    = 0
        self.phaseTwoImage       = None

    def update(self, dt, roomId, player):
        self.player = player

        if not self.desperation and self.enemy.hp <= self.maxHp * 0.15:
            self.startDesperation(player)
        elif self.phase == 1 and self.enemy.hp <= self.maxHp * 0.5:
            self.phase   = 2
            self.usePhaseTwoImage()

        if self.desperation:
            self.updateDesperation(dt, player)
        else:
            self.updateMovement(dt, roomId)
            self.updateQueue()

            match self.state:
                case "eye"       : self.updateEye(dt, player)
                case "brick"     : self.updateBrick(dt, player)
                case "pyramid"   : self.updatePyramid(dt, player)
                case "inverse"   : self.updateInverse(dt, player)
                case "calamitas" : self.updateCalamitas(dt, player)

        wallRects     = getWallRects(roomId, self.enemy.screenW, self.enemy.screenH)
        breakableData = getBreakableRectsWithCoords(roomId, self.enemy.screenW, self.enemy.screenH)

        def onBreak(r, c):
            breakTile(roomId, r, c)

        for b in list(self.bullets):
            if isinstance(b, explodingBullet) and b.rect.colliderect(player.rect):
                b.explode(self.bullets)
                continue

        self.bullets.update(
            dt,
            self.enemy.screenW,
            self.enemy.screenH,
            wallRects     = wallRects,
            breakableData = breakableData,
            onBreak       = onBreak,
        )

    def updateMovement(self, dt, roomId):
        if self.moveTimer  <= 0:
            marginX = int(const.scaleValue(120, self.screen[0], self.screen[1]))
            marginY = int(const.scaleValue(120, self.screen[0], self.screen[1]))
            self.moveTarget = pygame.Vector2(
                random.randint(marginX, self.enemy.screenW - marginX),
                random.randint(marginY, self.enemy.screenH - marginY),
            )
            self.moveTimer = random.uniform(0.5, 1.0)

        self.moveTimer -= dt
        direction = self.moveTarget - pygame.Vector2(self.enemy.rect.center)
        if direction.length() > 5:
            self.enemy.moveAndCollide(direction.normalize() * 310 * dt, roomId)

    def usePhaseTwoImage(self):
        if self.phaseTwoImage is None:
            self.phaseTwoImage = pygame.image.load(const.enemyPths["bossFourPhaseTwo"]).convert_alpha()
        center                 = self.enemy.rect.center
        self.enemy.image       = pygame.transform.scale(self.phaseTwoImage, self.enemy.image.get_size())
        self.enemy.rect        = self.enemy.image.get_rect(center=center)
        self.enemy.posX        = float(self.enemy.rect.x)
        self.enemy.posY        = float(self.enemy.rect.y)

    def updateQueue(self):
        if self.state is None and not self.queue:
            self.queue = ["eye", "brick", "pyramid", "inverse", "calamitas"]
            if self.phase == 2:
                self.queue += ["eye", "brick", "calamitas", "pyramid", "inverse"]
            random.shuffle(self.queue)

        if self.state is None and self.queue:
            self.state = self.queue.pop(0)
            getattr(self, f"start{self.state.capitalize()}")()

    def endState(self):
        if self.state == "eye":
            self.sniperBeam       = None
            self.sniperBeamActive = False
        self.state                = None
        self.data                 = {}
        self.warnPoints           = []

    def addBulletAtAngle(self, x, y, angle, speed = 0.7, size = (10, 10),
                         color=(255, 220, 50), damage=None, bounces=0):
        self.bullets.add(
            bullet(
                x, y,
                x + math.cos(angle) * 1000,
                y + math.sin(angle) * 1000,
                screen       = self.screen,
                difficulty   = self.difficulty,
                crossingTime = speed,
                size         = size,
                color        = color,
                damage       = self.enemy.atk if damage is None else damage,
                owner        = "enemy",
                maxBounces   = bounces,
            )
        )

    def aimAngle(self, source, target):
        return math.atan2(target[1] - source[1], target[0] - source[0])

    def startEye(self):
        ex, ey                = self.enemy.rect.center
        target                = pygame.Vector2(self.player.rect.center)
        self.data             = {
            "timer"     : 1.35,
            "fireTimer" : 0.22,
            "phase"     : "telegraph",
            "angle"     : self.aimAngle((ex, ey), target),
        }
        self.sniperBeam       = ((ex, ey), self.data["angle"])
        self.sniperBeamActive = False

    def updateEye(self, dt, player):
        ex, ey = self.enemy.rect.center
        d      = self.data

        if d["phase"]  == "telegraph":
            targetAngle = self.aimAngle((ex, ey), player.rect.center)
            diff        = math.atan2(math.sin(targetAngle - d["angle"]), math.cos(targetAngle - d["angle"]))
            d["angle"] += diff * 0.07
            self.sniperBeam = ((ex, ey), d["angle"])
            d["timer"] -= dt

            if d["timer"] <= 0:
                d["phase"] = "fire"
                self.sniperBeamActive = True

        elif d["phase"] == "fire":
            self.sniperBeam = ((ex, ey), d["angle"])
            d["fireTimer"] -= dt
            if d["fireTimer"] <= 0:
                self.endState()

    def startBrick(self):
        start = pygame.Vector2(self.enemy.rect.center)

        scaledRect = const.scaleSize((92, 62), self.screen[0], self.screen[1])
        self.data = {
            "timer": 4.5,
            "pos": start,
            "rect": pygame.Rect(0, 0, scaledRect[0], scaledRect[1]),
            "velocity": pygame.Vector2(0, 0),
            "state": "aim",
            "pauseTimer": 0.0,
            "burstsFired": 0,
            "burstTotal": 3 if self.phase == 1 else 6,
        }
        self.data["rect"].center = start

    def updateBrick(self, dt, player):
        self.data["timer"] -= dt

        if self.data["state"] == "aim":
            target = pygame.Vector2(player.rect.center)
            direction = target - self.data["pos"]

            if direction.length() == 0:
                direction = pygame.Vector2(1, 0)

            speedFactor = const.getScreenScaleFactor(self.screen[0], self.screen[1])
            self.data["velocity"] = direction.normalize() * (680 * speedFactor)
            self.spawnAftonCircle()
            self.data["burstsFired"] += 1
            self.data["state"] = "dash"

        move = self.data["velocity"] * dt
        self.data["pos"] += move
        self.data["rect"].center = self.data["pos"]

        wallRects = getWallRects(-3, self.enemy.screenW, self.enemy.screenH)
        hitWall   = False

        for wall in wallRects:
            if self.data["rect"].colliderect(wall):
                hitWall = True
                break

        if self.data["state"] == "dash" and hitWall:
            if self.data["burstsFired"] >= self.data["burstTotal"]:
                self.endState()
                return

            self.data["velocity"]   = pygame.Vector2(0, 0)
            self.data["pauseTimer"] = 0.18
            self.data["state"]      = "pause"

        if self.data["state"]          == "pause":
            self.data["pauseTimer"]    -= dt

            if self.data["pauseTimer"] <= 0:
                self.data["state"]      = "aim"

        if self.data["timer"] <= 0:
            self.endState()

    def spawnAftonCircle(self):
        x, y = self.data["pos"]
        count = 18 if self.phase == 1 else 24
        for i in range(count):
            angle = math.tau * i / count
            self.addBulletAtAngle(x, y, angle, speed=0.6, size=(12, 12), color=(145, 0, 210), damage=self.enemy.atk)

    def startPyramid(self):
        self.data = {"timer": 1.4, "shotTimer": 0.0, "lagTarget": pygame.Vector2(self.player.rect.center)}

    def updatePyramid(self, dt, player):
        self.data["timer"]        -= dt
        self.data["shotTimer"]    -= dt
        if self.data["shotTimer"] <= 0:
            ex, ey = self.enemy.rect.center
            base   = self.aimAngle((ex, ey), player.rect.center)
            for offset in (-10, 0, 10):
                self.bullets.add(
                    triangleShot(
                        ex, ey,
                        base + math.radians(offset),
                        460 * self.difficulty,
                        self.enemy.atk,
                        self.screen,
                        shootsEyes = self.phase == 2,
                        target     = pygame.Vector2(self.data["lagTarget"]),
                    )
                )
            if self.phase == 2:
                self.data["lagTarget"] = pygame.Vector2(player.rect.center)
            self.data["shotTimer"] = 0.33

        for tri in [b for b in self.bullets if isinstance(b, triangleShot) and b.shootsEyes and b.eyeTimer <= 0]:
            target = tri.target if tri.target is not None else pygame.Vector2(player.rect.center)
            self.bullets.add(
                delayedAimBullet(
                    tri.rect.centerx, tri.rect.centery, target.x, target.y,
                    screen      = self.screen,
                    difficulty  = self.difficulty,
                    delay       = 0.22,
                    crossingTime= 0.58,
                    size        = (24, 16),
                    color       = (255, 55, 55),
                    damage      = self.enemy.atk,
                    owner       = "enemy",
                )
            )
            tri.eyeTimer        = 1

        if self.data["timer"] <= 0:
            self.endState()

    def startInverse(self):
        self.data = {"timer": 2.5}
        self.player.invertedControlsTimer = max(self.player.invertedControlsTimer, 2.5)

    def updateInverse(self, dt, player):
        self.data["timer"] -= dt
        if self.data["timer"] <= 0:
            self.endState()

    def startCalamitas(self):
        spots = 9 if self.phase == 1 else 14
        margin = int(const.scaleValue(90, self.screen[0], self.screen[1]))
        self.warnPoints = [
            (random.randint(margin, self.enemy.screenW - margin), random.randint(margin, self.enemy.screenH - margin))
            for _ in range(spots)
        ]
        self.data = {"timer": 0.9, "fired": False}

    def updateCalamitas(self, dt, player):
        self.data["timer"]    -= dt
        if self.data["timer"] <= 0 and not self.data["fired"]:
            for idx, (x, y) in enumerate(self.warnPoints):
                if idx % 3 == 0:
                    base = self.aimAngle((x, y), player.rect.center) if self.phase == 2 else (
                        random.uniform(0, math.tau))
                    for offset in (-32, -16, 0, 16, 32):
                        self.addBulletAtAngle(
                            x, y,
                            base + math.radians(offset),
                            speed  = 0.67,
                            size   = (9, 9),
                            color  = (255, 125, 0),
                            damage = self.enemy.atk,
                        )
                else:
                    angle = self.aimAngle((x, y),
                                          player.rect.center) if self.phase == 2 else random.uniform(0, math.tau)
                    self.addBulletAtAngle(x, y, angle, speed=0.68, size=(9, 9), color=(255, 125, 0), damage=self.enemy.atk)
            self.data["fired"] = True
            self.endState()

    def startDesperation(self, player):
        self.desperation       = True
        self.desperationTimer  = self.desperationDuration
        self.state             = None
        self.queue.clear()
        self.enemy.rect.center = (self.enemy.screenW // 2, self.enemy.screenH // 2)
        self.enemy.syncPos     = getattr(self.enemy, "syncPos", None)
        self.enemy.posX        = float(self.enemy.rect.x)
        self.enemy.posY        = float(self.enemy.rect.y)
        center                 = self.enemy.rect.center
        self.lasers            = [(center, angle) for angle in (0, 60, 120)]
        self.data              = {"shotgunTimer": 10.0, "explodeTimer": 0.35}

    def updateDesperation(self, dt, player):
        self.desperationTimer -= dt
        ex, ey                 = self.enemy.rect.center
        base                   = self.aimAngle((ex, ey),
                                               player.rect.center)

        self.data["explodeTimer"]    -= dt
        if self.data["explodeTimer"] <= 0 and self.desperationTimer >= 15:
            self.bullets.add(
                explodingBullet(
                    ex, ey,
                    player.rect.centerx, player.rect.centery,
                    screen       = self.screen,
                    difficulty   = self.difficulty,
                    crossingTime = 0.52,
                    size         = (14, 14),
                    color        = (255, 120, 30),
                    damage       = self.enemy.atk,
                    owner        = "enemy",
                    childCount   = 20,
                )
            )
            self.data["explodeTimer"] = 0.45

        self.data["shotgunTimer"]    -= dt
        if self.data["shotgunTimer"] <= 0:
            for a in (-18, 0, 18):
                self.addBulletAtAngle(ex, ey, base + math.radians(a),
                                      speed   = 0.64, size = (9, 9), damage = self.enemy.atk,
                                      bounces = 5)
            self.data["shotgunTimer"] = 0.55

        if self.desperationTimer <= 0:
            self.enemy.hp = 0
            self.enemy.kill()

    def beamHitsPlayer(self, player):
        sniperThreshold = const.scaleValue(11, self.screen[0], self.screen[1])
        desperationThreshold = const.scaleValue(9, self.screen[0], self.screen[1])

        if self.sniperBeamActive and self.sniperBeam is not None:
            start, angle = self.sniperBeam
            if self.distanceToBeam(player.rect.center, start, angle) <= sniperThreshold:
                return True

        if not self.desperation or self.desperationTimer < 15:
            return False

        for start, angleDeg in self.lasers:
            if self.distanceToBeam(player.rect.center, start, math.radians(angleDeg)) <= desperationThreshold:
                return True
        return False

    def distanceToBeam(self, point, start, angle):
        px, py = point
        sx, sy = start
        dx, dy = math.cos(angle), math.sin(angle)
        return abs((px - sx) * dy - (py - sy) * dx)

    def draw(self, screen):
        self.bullets.draw(screen)

        if self.warnPoints:
            surf = pygame.Surface((self.enemy.screenW, self.enemy.screenH), pygame.SRCALPHA)
            warnRadius = int(const.scaleValue(14, self.screen[0], self.screen[1]))
            warnWidth = max(1, int(const.scaleValue(2, self.screen[0], self.screen[1])))
            for x, y in self.warnPoints:
                pygame.draw.circle(surf, (*const.blue[:3], 140), (x, y), warnRadius, warnWidth)
            screen.blit(surf, (0, 0))

        if self.state == "brick" and self.data:
            x, y = self.data["pos"]
            brickSize = const.scaleSize((76, 52), self.screen[0], self.screen[1])
            pygame.draw.rect(screen, (120, 0, 170), pygame.Rect(x - brickSize[0]//2, y - brickSize[1]//2, brickSize[0], brickSize[1]))

        if self.sniperBeam is not None:
            start, angle = self.sniperBeam
            end = (start[0] + math.cos(angle) * 3000, start[1] + math.sin(angle) * 3000)
            color = (255, 0, 0, 220) if self.sniperBeamActive else (255, 40, 40, 90)
            beamWidth = int(const.scaleValue(9 if self.sniperBeamActive else 3, self.screen[0], self.screen[1]))
            beamWidth = max(1, beamWidth)
            pygame.draw.line(screen, color, start, end, beamWidth)

        if self.desperation and self.desperationTimer >= 15:
            surf = pygame.Surface((self.enemy.screenW, self.enemy.screenH), pygame.SRCALPHA)
            laserWidth = max(1, int(const.scaleValue(10, self.screen[0], self.screen[1])))
            for start, angleDeg in self.lasers:
                angle = math.radians(angleDeg)
                end1 = (start[0] + math.cos(angle) * 3000, start[1] + math.sin(angle) * 3000)
                end2 = (start[0] - math.cos(angle) * 3000, start[1] - math.sin(angle) * 3000)
                pygame.draw.line(surf, (255, 0, 0, 160), end1, end2, laserWidth)
            screen.blit(surf, (0, 0))
