import math
import random
import pygame
import const
from entity.weapons.bullet import bullet
from mapping.maps import getWallRects, getBreakableRectsWithCoords, breakTile

class explodingBullet(bullet):
    def __init__(self, *args, childCount=5, childColor=(255, 120, 40), timer=0.0, **kwargs):
        super().__init__(*args, **kwargs)
        self.childCount   = childCount
        self.childColor   = childColor
        self.explodeTimer = timer

    def update(self, deltaTime, screenW, screenH, wallRects=None, breakableData=None, onBreak=None):
        if self.explodeTimer > 0:
            self.explodeTimer -= deltaTime
            if self.explodeTimer <= 0:
                self.explode()
                return
        super().update(deltaTime, screenW, screenH, wallRects, breakableData, onBreak)

    def explode(self, group=None):
        x, y = self.rect.center
        target = group if group is not None else self.groups()[0]
        for i in range(self.childCount):
            angle = math.tau * i / self.childCount
            target.add(
                bullet(
                    x, y,
                    x + math.cos(angle) * 160,
                    y + math.sin(angle) * 160,
                    screen       = self.screen, difficulty=0.9,
                    crossingTime = 0.55, size=(7, 7),
                    color        = self.childColor, damage=self.damage, owner="enemy",
                )
            )
        self.kill()

class beamSpinner:
    def __init__(self, cx, cy, angle, speed, length):
        self.cx     = cx
        self.cy     = cy
        self.angle  = angle
        self.speed  = speed
        self.length = length

    def update(self, dt):
        self.angle += self.speed * dt

    def getEndpoints(self):
        ex = self.cx + math.cos(self.angle) * self.length
        ey = self.cy + math.sin(self.angle) * self.length
        ox = self.cx - math.cos(self.angle) * self.length
        oy = self.cy - math.sin(self.angle) * self.length
        return (ex, ey), (ox, oy)

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
                target    = pygame.Vector2(self.aim)
                direction = target - pygame.Vector2(self.rect.center)
                if direction.length() > 0:
                    self.velocity = direction.normalize() * (self.savedCrossingTime * self.screen[0]) * self.savedDifficulty
            return
        super().update(deltaTime, screenW, screenH, wallRects, breakableData, onBreak)

class triangleShot(pygame.sprite.Sprite):
    def __init__(self, x, y, angle, speed, damage, screen, shootsEyes=False, target=None):
        super().__init__()
        self.image      = pygame.Surface((74, 64), pygame.SRCALPHA)
        pts             = [(37, 2), (4, 60), (70, 60)]
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

class lanceProjectile(pygame.sprite.Sprite):
    def __init__(self, x, y, angle, screen, difficulty, enemyAtk, bulletsGroup, playerRef, phase):
        super().__init__()
        self.pos          = pygame.Vector2(x, y)
        self.angle        = angle
        self.speed        = 420 if phase == 1 else (520 if phase == 2 else 620)
        self.velocity     = pygame.Vector2(math.cos(angle), math.sin(angle)) * self.speed
        self.image        = pygame.Surface((14, 14), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (255, 200, 80), (7, 7), 7)
        self.rect         = self.image.get_rect(center=(x, y))
        self.screen       = screen
        self.difficulty   = difficulty
        self.atk          = enemyAtk
        self.damage       = enemyAtk
        self.owner        = "enemy"
        self.spawnTimer   = 0.0
        self.bulletsGroup = bulletsGroup
        self.playerRef    = playerRef
        self.life         = 4.0
        self.phase        = phase

    def update(self, dt, screenW, screenH, wallRects=None, breakableData=None, onBreak=None):
        self.life -= dt
        self.pos += self.velocity * dt
        self.rect.center = self.pos
        self.spawnTimer -= dt
        if self.spawnTimer <= 0:
            self.spawnTimer = (0.6 if self.phase == 1 else (0.4 if self.phase == 2 else 0.28))
            for a in (0, math.pi / 2):
                b = bullet(
                    self.rect.centerx, self.rect.centery,
                    self.rect.centerx + math.cos(a) * 1000,
                    self.rect.centery + math.sin(a) * 1000,
                    screen       = self.screen, difficulty=self.difficulty,
                    crossingTime = 0.6, size=(9, 9), color=(255, 150, 40), owner="enemy", maxBounces=1, damage=self.atk,
                )
                self.bulletsGroup.add(b)
            if self.playerRef is not None:
                aim = math.atan2(
                    self.playerRef.rect.centery - self.rect.centery,
                    self.playerRef.rect.centerx - self.rect.centerx,
                )
                for _ in range(2 + (1 if self.phase >= 3 else 0)):
                    b = bullet(
                        self.rect.centerx, self.rect.centery,
                        self.rect.centerx + math.cos(aim) * 1000,
                        self.rect.centery + math.sin(aim) * 1000,
                        screen       = self.screen, difficulty=self.difficulty,
                        crossingTime = 0.6, size=(9, 9), color=(255, 90, 40), owner="enemy",
                    )
                    self.bulletsGroup.add(b)

        if (self.rect.right < 0 or self.rect.left > screenW or self.rect.bottom < 0 or self.rect.top > screenH) or self.life <= 0:
            self.kill()
            return
        if wallRects:
            for wall in wallRects:
                if self.rect.colliderect(wall):
                    self.kill()
                    return

class orbitShield:
    def __init__(self, angle):
        self.angle  = angle
        self.radius = 120
        self.hp     = 60

class bossSixAIClass:
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
        self.spinners            = []
        self.beamSpinners        = []
        self.eyeLaser            = None
        self.sniperBeam          = None
        self.sniperBeamActive    = False
        self.desperation         = False
        self.desperationDuration = 60.0
        self.desperationTimer    = 0.0
        self.desperationStage    = 0
        self.moveTarget          = pygame.Vector2(enemy.rect.center)
        self.moveTimer           = 0.0
        self.phaseTwoImage       = None
        self.phaseThreeImage     = None
        self.phaseName           = "NagRAH"
        self.syncPos             = None
        self.shieldActive        = False
        self.shields             = []
        self.splitterActive      = False
        self.splitterTimer       = 0.0
        self.splitterBeams       = []
        self.pendingWarns        = []
        self.warnDirLines        = []

    def update(self, dt, roomId, player):
        self.player = player
        ex, ey = self.enemy.rect.center

        if not self.desperation and self.enemy.hp <= self.maxHp * 0.15:
            self.startDesperation()
        elif self.phase == 1 and self.enemy.hp <= self.maxHp * 0.66:
            self.phase = 2
            self.usePhaseTwoImage()
            self.activateShields()
        elif self.phase == 2 and self.enemy.hp <= self.maxHp * 0.33:
            self.phase = 3
            self.usePhaseThreeImage()
            self.deactivateShields()

        if self.desperation:
            self.updateDesperation(dt, player, ex, ey)
        else:
            self.updateMovement(dt, roomId)
            self.updateQueue()
            self.updateEyeLaser(dt, player, ex, ey)

            match self.state:
                case "circleShot"   : self.updateCircleShot(dt, player, ex, ey)
                case "bulletHell"   : self.updateBulletHell(dt, player, ex, ey)
                case "summonSpinner": self.updateSummonSpinner(dt, player, ex, ey)
                case "powerShot"    : self.updatePowerShot(dt, player, ex, ey)
                case "isolate"      : self.updateIsolate(dt, player, ex, ey)
                case "rainFire"     : self.updateRainFire(dt, player, ex, ey)
                case "eye"          : self.updateEye(dt, player, ex, ey)
                case "brick"        : self.updateBrick(dt, player, ex, ey)
                case "calamitas"    : self.updateCalamitas(dt, player, ex, ey)
                case "pyramid"      : self.updatePyramid(dt, player, ex, ey)
                case "beamDance"    : self.updateBeamDance(dt, player, ex, ey)
                case "powerOfRah"   : self.updatePowerOfRah(dt, player, ex, ey)
                case "wallsOfRah"   : self.updateWallsOfRah(dt, player, ex, ey)
                case "lanceOfRah"   : self.updateLanceOfRah(dt, player, ex, ey)

        self.processPendingWarns(dt)

        if self.splitterActive:
            self.updateSplitter(dt, player, ex, ey)

        if self.phase == 2 and self.shieldActive:
            self.updateShields(dt)

        wallRects     = getWallRects(roomId, self.enemy.screenW, self.enemy.screenH)
        breakableData = getBreakableRectsWithCoords(roomId, self.enemy.screenW, self.enemy.screenH)

        def onBreak(r, c):
            breakTile(roomId, r, c)

        for b in list(self.bullets):
            if isinstance(b, explodingBullet) and b.explodeTimer <= 0 and b.rect.colliderect(player.rect):
                b.explode(self.bullets)
                continue

        self.bullets.update(
            dt, self.enemy.screenW, self.enemy.screenH,
            wallRects=wallRects, breakableData=breakableData, onBreak=onBreak,
        )

    def activateShields(self):
        self.shieldActive = True
        self.shields      = []
        for i in range(5):
            self.shields.append(orbitShield(math.radians(i * 72)))

    def deactivateShields(self):
        self.shieldActive = False
        self.shields      = []

    def updateShields(self, dt):
        ex, ey = self.enemy.rect.center
        for i, shield in enumerate(self.shields):
            shield.angle += dt * (2.2 if i % 2 == 0 else -1.6)
            shield.x = ex + math.cos(shield.angle) * shield.radius
            shield.y = ey + math.sin(shield.angle) * shield.radius

    def shieldBlocksBullet(self, bulletSprite):
        if not self.shieldActive or not self.shields:
            return False
        bx, by = bulletSprite.rect.center
        bpos = pygame.Vector2(bx, by)
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

    def updateMovement(self, dt, roomId):
        if self.moveTimer <= 0:
            marginX         = int(const.scaleValue(120, self.screen[0], self.screen[1]))
            marginY         = int(const.scaleValue(120, self.screen[0], self.screen[1]))
            self.moveTarget = pygame.Vector2(
                random.randint(marginX, self.enemy.screenW - marginX),
                random.randint(marginY, self.enemy.screenH - marginY),
            )
            self.moveTimer = random.uniform(0.8, 1.5)
        self.moveTimer -= dt
        direction = self.moveTarget - pygame.Vector2(self.enemy.rect.center)
        if direction.length() > 5:
            self.enemy.moveAndCollide(direction.normalize() * 260 * dt, roomId)

    def usePhaseTwoImage(self):
        if self.phaseTwoImage is None:
            self.phaseTwoImage = pygame.image.load(const.enemyPths["bossSixTwo"]).convert_alpha()
        center             = self.enemy.rect.center
        self.enemy.image   = pygame.transform.scale(self.phaseTwoImage, self.enemy.image.get_size())
        self.enemy.rect    = self.enemy.image.get_rect(center=center)
        self.enemy.posX    = float(self.enemy.rect.x)
        self.enemy.posY    = float(self.enemy.rect.y)

    def usePhaseThreeImage(self):
        if self.phaseThreeImage is None:
            self.phaseThreeImage = pygame.image.load(const.enemyPths["bossSixThree"]).convert_alpha()
        center               = self.enemy.rect.center
        self.enemy.image     = pygame.transform.scale(self.phaseThreeImage, self.enemy.image.get_size())
        self.enemy.rect      = self.enemy.image.get_rect(center=center)
        self.enemy.posX      = float(self.enemy.rect.x)
        self.enemy.posY      = float(self.enemy.rect.y)

    def updateQueue(self):
        if self.state is None and not self.queue:
            self.queue = ["circleShot", "bulletHell", "summonSpinner", "powerShot"]
            if self.phase >= 1:
                self.queue += ["eye", "brick", "calamitas", "pyramid", "beamDance", "powerOfRah"]
            if self.phase >= 2:
                self.queue += ["isolate", "wallsOfRah"]
            if self.phase >= 3:
                self.queue += ["rainFire", "lanceOfRah"]
            self.queue += ["splitter"]
            random.shuffle(self.queue)

        if self.state is None and self.queue:
            name = self.queue.pop(0)
            if name == "splitter":
                self.startSplitter()
                return
            self.state = name
            getattr(self, f"start{name[0].upper() + name[1:]}", lambda: None)()

    def endState(self):
        self.state            = None
        self.data             = {}
        self.warnPoints       = []
        self.spinners         = []
        self.beamSpinners     = []
        self.sniperBeam       = None
        self.sniperBeamActive = False
        self.lasers           = []
        self.pendingWarns     = []

    def addBulletAtAngle(self, x, y, angle, speed=0.7, size=(10, 10), color=(255, 220, 50), damage=None, bounces=0, ignoreWalls=False):
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
                ignoreWalls  = ignoreWalls,
            )
        )

    def aimAngle(self, source, target):
        return math.atan2(target[1] - source[1], target[0] - source[0])

    def addWarnedSpawn(self, warnPoints, fireFunc, delay=0.35):
        for p in warnPoints:
            self.warnPoints.append(p)
        self.pendingWarns.append({"timer": delay, "fireFunc": fireFunc})

    def processPendingWarns(self, dt):
        for pw in list(self.pendingWarns):
            pw["timer"] -= dt
            if pw["timer"] <= 0:
                pw["fireFunc"]()
                self.pendingWarns.remove(pw)

    def updateEyeLaser(self, dt, player, ex, ey):
        if self.state not in ("circleShot", "summonSpinner"):
            return
        if self.eyeLaser is None:
            tele          = 1.2
            hold          = 0.6
            fire          = 1.2
            reload        = 0.8
            targetAngle   = self.aimAngle((ex, ey), player.rect.center)
            self.eyeLaser = {
            "start":         (ex, ey),
            "currentAngle":  targetAngle,
            "targetAngle":   targetAngle,
            "stage":         "tele",
            "stageTimer":    tele,
            "tele":          tele,
            "hold":          hold,
            "fire":          fire,
            "reload":        reload,
            "aimInterp":     0.5,
            "spawnTimer":    0.0,
            "spawnInterval": 0.9,
            }
        else:
            self.eyeLaser["start"] = (ex, ey)
            self.eyeLaser["targetAngle"] = self.aimAngle((ex, ey), player.rect.center)
            aimInterp = {1: 0.5, 2: 0.8, 3: 1.2}.get(self.phase, 0.5)
            self.eyeLaser["aimInterp"] = aimInterp
            self.eyeLaser["stageTimer"] -= dt
            if self.eyeLaser["stageTimer"] <= 0:
                s = self.eyeLaser["stage"]
                if s == "tele":
                    self.eyeLaser["stage"] = "hold"
                    self.eyeLaser["stageTimer"] = self.eyeLaser["hold"]
                elif s == "hold":
                    self.eyeLaser["stage"] = "fire"
                    self.eyeLaser["stageTimer"] = self.eyeLaser["fire"]
                elif s == "fire":
                    self.eyeLaser["stage"] = "reload"
                    self.eyeLaser["stageTimer"] = self.eyeLaser["reload"]
                elif s == "reload":
                    self.eyeLaser["stage"] = "tele"
                    self.eyeLaser["stageTimer"] = self.eyeLaser["tele"]

            if self.eyeLaser["stage"] in ("tele", "hold"):
                cur  = self.eyeLaser["currentAngle"]
                tgt  = self.eyeLaser["targetAngle"]
                diff = math.atan2(math.sin(tgt - cur), math.cos(tgt - cur))
                self.eyeLaser["currentAngle"] += diff * self.eyeLaser["aimInterp"] * dt * 60


    def startCircleShot(self):
        self.data = {
            "timer":            4.5,
            "circleTimer":      0.0,
            "circleInterval":   0.7,
            "shotgunTimer":     0.0,
            "shotgunInterval":  1.2,
            "brickTimer":       0.0,
            "brickInterval":    1.0,
        }

    def updateCircleShot(self, dt, player, ex, ey):
        d = self.data
        d["timer"] -= dt
        d["circleTimer"] -= dt
        if d["circleTimer"] <= 0:
            self.spawnCircleBullets(player)
            d["circleTimer"] = d["circleInterval"]
        if self.phase >= 2:
            d["shotgunTimer"] -= dt
            if d["shotgunTimer"] <= 0:
                self.addWarnedSpawn([(ex, ey)], lambda ex=ex, ey=ey: self.fireShotgun(ex, ey, self.player), 0.35)
                d["shotgunTimer"] = d["shotgunInterval"]
        if self.phase >= 3:
            d["brickTimer"] -= dt
            if d["brickTimer"] <= 0:
                self.addWarnedSpawn([(ex, ey)], lambda ex=ex, ey=ey: self.spawnBulletBrick(ex, ey, self.player, childCount=4), 0.35)
                d["brickTimer"] = d["brickInterval"]
        if d["timer"] <= 0:
            self.eyeLaser = None
            self.endState()

    def warnCircleBullets(self, player):
        px, py = player.rect.center
        count           = 10
        radius          = int(const.scaleValue(160, self.screen[0], self.screen[1]))
        self.warnPoints = []
        for i in range(count):
            angle = math.tau * i / count
            bx    = px + math.cos(angle) * radius
            by    = py + math.sin(angle) * radius
            self.warnPoints.append((int(bx), int(by)))
        self.data["warnTimer"] = 0.35
        self.data["pendingCircle"] = True

    def spawnCircleBullets(self, player):
        px, py = player.rect.center
        count  = 10
        radius = int(const.scaleValue(160, self.screen[0], self.screen[1]))
        for i in range(count):
            angle  = math.tau * i / count
            bx     = px + math.cos(angle) * radius
            by     = py + math.sin(angle) * radius
            inward = self.aimAngle((bx, by), player.rect.center)
            self.addBulletAtAngle(bx, by, inward, speed=0.3, size=(8, 8), color=(255, 80, 80))

    def fireShotgun(self, ex, ey, player):
        base = self.aimAngle((ex, ey), player.rect.center)
        for spread in (-20, -8, 8, 20):
            self.addBulletAtAngle(ex, ey, base + math.radians(spread), speed=0.5, size=(7, 7), color=(255, 180, 60))

    def prFirePowerShotgun(self, ex, ey, player):
        base = self.aimAngle((ex, ey), player.rect.center)
        for spread in (-15, -5, 5, 15):
            self.addBulletAtAngle(ex, ey, base + math.radians(spread), speed=0.55, size=(9, 9), color=(255, 100, 100), bounces=1)

    def spawnBulletBrick(self, bx, by, player, childCount=8):
        base = self.aimAngle((bx, by), player.rect.center)
        for i in range(childCount):
            self.addBulletAtAngle(bx, by, base + math.radians(i * (360 / childCount)), speed=0.4, size=(11, 11), color=(200, 60, 200))

    def startBulletHell(self):
        self.data = {
            "timer":             3.5,
            "burstTimer":        0.0,
            "burstInterval":     0.4,
            "warnTimer":         0.3,
            "explodingTimer":    0.0,
            "explodingInterval": 1.2,
            "brickTimer":        0.0,
            "brickInterval":     1.5,
            "pendingBurst":      False,
            "pendingPositions":  [],
        }

    def updateBulletHell(self, dt, player, ex, ey):
        d = self.data
        d["timer"] -= dt
        d["burstTimer"] -= dt
        if d["burstTimer"] <= 0:
            self.warnRandomBurst(player)
            d["burstTimer"] = d["burstInterval"]
        if d.get("warnTimer", 0) > 0:
            d["warnTimer"] -= dt
            if d["warnTimer"] <= 0 and d.get("pendingBurst"):
                d["pendingBurst"] = False
                self.spawnWarnedBullets(d)
        if self.phase >= 2:
            d["explodingTimer"] -= dt
            if d["explodingTimer"] <= 0:
                self.addWarnedSpawn([(random.randint(100, self.enemy.screenW - 100), random.randint(100, self.enemy.screenH - 100))], lambda: self.spawnExplodingBullet(self.player), 0.35)
                d["explodingTimer"] = d["explodingInterval"]
        if self.phase >= 3:
            d["brickTimer"] -= dt
            if d["brickTimer"] <= 0:
                sx = random.randint(50, self.enemy.screenW - 50)
                sy = random.randint(50, self.enemy.screenH - 50)
                self.addWarnedSpawn([(sx, sy)], lambda sx=sx, sy=sy: self.spawnBulletBrick(sx, sy, self.player, childCount=6), 0.35)
                d["brickTimer"] = d["brickInterval"]
        if d["timer"] <= 0:
            self.endState()

    def warnRandomBurst(self, player):
        margin    = int(const.scaleValue(60, self.screen[0], self.screen[1]))
        count     = 4
        positions = []
        for _ in range(count):
            bx = random.randint(margin, self.enemy.screenW - margin)
            by = random.randint(margin, self.enemy.screenH - margin)
            positions.append((bx, by))
            self.warnPoints.append((bx, by))
        self.data["pendingBurst"] = True
        self.data["pendingPositions"] = positions
        self.data["warnTimer"] = 0.35

    def spawnWarnedBullets(self, d):
        self.warnPoints = []
        for bx, by in d.get("pendingPositions", []):
            tx = random.randint(50, self.enemy.screenW - 50)
            ty = random.randint(50, self.enemy.screenH - 50)
            self.bullets.add(
                bullet(
                    bx, by, tx, ty,
                    screen       = self.screen, difficulty=self.difficulty,
                    crossingTime = 0.65, size=(7, 7), color=(255, 200, 100),
                    damage       = self.enemy.atk, owner="enemy",
                )
            )

    def spawnExplodingBullet(self, player):
        margin = int(const.scaleValue(100, self.screen[0], self.screen[1]))
        bx     = random.randint(margin, self.enemy.screenW - margin)
        by     = random.randint(margin, self.enemy.screenH - margin)
        self.bullets.add(
            explodingBullet(
                bx, by, player.rect.centerx, player.rect.centery,
                screen       = self.screen, difficulty=self.difficulty,
                crossingTime = 0.6, size=(16, 16), color=(255, 80, 40),
                damage       = self.enemy.atk, owner="enemy",
                childCount   = 5,
                timer        = 1.8,
            )
        )

    def startSummonSpinner(self):
        cx, cy = self.enemy.rect.center
        length            = max(self.enemy.screenW, self.enemy.screenH) * 0.6
        self.beamSpinners = [
            beamSpinner(cx, cy, 0, math.radians(20), length),
            beamSpinner(cx, cy, math.pi, math.radians(-20), length),
        ]
        self.data = {
            "timer":              4.5,
            "shotgunTimer":       0.0,
            "shotgunInterval":    1.5,
            "eyeTimer":           0.0,
            "eyeInterval":        3.0,
            "machineGunTimer":    0.0,
            "machineGunInterval": 0.08,
        }

    def updateSummonSpinner(self, dt, player, ex, ey):
        d = self.data
        d["timer"] -= dt
        for bs in self.beamSpinners:
            bs.update(dt)
        if self.phase >= 2:
            d["shotgunTimer"] -= dt
            if d["shotgunTimer"] <= 0:
                self.addWarnedSpawn([(ex, ey)], lambda ex=ex, ey=ey: self.fireShotgun(ex, ey, self.player), 0.35)
                d["shotgunTimer"] = d["shotgunInterval"]
        if self.phase >= 3:
            d["machineGunTimer"] -= dt
            if d["machineGunTimer"] <= 0:
                base = self.aimAngle((ex, ey), player.rect.center)
                self.addBulletAtAngle(ex, ey, base + math.radians(random.uniform(-12, 12)), speed=0.4, size=(5, 5), color=(255, 200, 60))
                d["machineGunTimer"] = d["machineGunInterval"]
        if d["timer"] <= 0:
            self.eyeLaser = None
            self.endState()

    def startPowerShot(self):
        self.data = {
            "timer":              4.0,
            "brickTimer":         0.0,
            "brickInterval":      1.0,
            "machineGunTimer":    0.0,
            "machineGunInterval": 0.06,
            "shotgunTimer":       0.0,
            "shotgunInterval":    0.7,
            "smallBrickTimer":    0.0,
            "smallBrickInterval": 0.9,
        }

    def updatePowerShot(self, dt, player, ex, ey):
        d = self.data
        d["timer"] -= dt
        d["brickTimer"] -= dt
        if d["brickTimer"] <= 0:
            self.addWarnedSpawn([(ex, ey)], lambda ex=ex, ey=ey: self.spawnBulletBrick(ex, ey, self.player, childCount=8), 0.35)
            d["brickTimer"] = d["brickInterval"]
        if self.phase >= 2:
            d["machineGunTimer"] -= dt
            if d["machineGunTimer"] <= 0:
                base = self.aimAngle((ex, ey), player.rect.center)
                self.addBulletAtAngle(ex, ey, base + math.radians(random.uniform(-8, 8)), speed=0.35, size=(5, 5), color=(255, 220, 80))
                d["machineGunTimer"] = d["machineGunInterval"]
            d["shotgunTimer"] -= dt
            if d["shotgunTimer"] <= 0:
                self.addWarnedSpawn([(ex, ey)], lambda ex=ex, ey=ey: self.prFirePowerShotgun(ex, ey, self.player), 0.35)
                d["shotgunTimer"] = d["shotgunInterval"]
        if self.phase >= 3:
            d["smallBrickTimer"] -= dt
            if d["smallBrickTimer"] <= 0:
                self.addWarnedSpawn([(ex, ey)], lambda ex=ex, ey=ey: self.spawnBulletBrick(ex, ey, self.player, childCount=5), 0.35)
                d["smallBrickTimer"] = d["smallBrickInterval"]
        if d["timer"] <= 0:
            self.endState()

    def startIsolate(self):
        self.data = {
            "timer":            4.5,
            "fillTimer":        0.0,
            "fillInterval":     1.5,
            "vTipX":            0.0,
            "vDirection":       1,
            "vSpeed":           100.0,
            "meatballTimer":    0.0,
            "meatballInterval": 2.0,
        }

    def updateIsolate(self, dt, player, ex, ey):
        d = self.data
        d["timer"] -= dt
        d["vTipX"] += d["vSpeed"] * d["vDirection"] * dt
        if d["vTipX"] > self.enemy.screenW:
            d["vTipX"] = self.enemy.screenW
            d["vDirection"] = -1
        elif d["vTipX"] < 0:
            d["vTipX"] = 0
            d["vDirection"] = 1
        d["fillTimer"] -= dt
        if d["fillTimer"] <= 0:
            self.fillMapWithGap(d)
            d["fillTimer"] = d["fillInterval"]
        if self.phase >= 3:
            d["meatballTimer"] -= dt
            if d["meatballTimer"] <= 0:
                bx = random.randint(60, self.enemy.screenW - 60)
                self.addWarnedSpawn([(bx, 20)], lambda bx=bx: self.fireMeatball(bx=bx, player=self.player), 0.35)
                d["meatballTimer"] = d["meatballInterval"]
        if d["timer"] <= 0:
            self.endState()

    def fillMapWithGap(self, d):
        sw, sh   = self.enemy.screenW, self.enemy.screenH
        margin   = int(const.scaleValue(100, self.screen[0], self.screen[1]))
        spacing  = int(const.scaleValue(130, self.screen[0], self.screen[1]))
        vTipX    = d["vTipX"]
        vWidth   = int(const.scaleValue(180, self.screen[0], self.screen[1]))
        positions = []
        dirLines  = []
        for x in range(margin, sw - margin, spacing):
            for y in range(margin, sh - margin, spacing):
                if self.inVShape(x, y, vTipX, sw, vWidth):
                    continue
                positions.append((x, y))
                tx = x + random.randint(-80, 80)
                ty = y + random.randint(-80, 80)
                dirLines.append(((x, y), (tx, ty)))
        self.warnDirLines = dirLines
        self.addWarnedSpawn(positions, lambda dl=dirLines: self.prFireFillGap(dl), 0.5)

    def prFireFillGap(self, dirLines):
        for (x, y), (tx, ty) in dirLines:
            self.bullets.add(
                bullet(
                    x, y, tx, ty,
                    screen       = self.screen, difficulty=self.difficulty,
                    crossingTime = 3.0, size=(6, 6), color=(150, 60, 200),
                    damage       = self.enemy.atk, owner="enemy",
                )
            )
        self.warnDirLines = []

    def inVShape(self, x, y, vTipX, screenW, vWidth):
        halfW     = screenW // 2
        leftEdge  = vTipX - vWidth * (1 - abs(x - halfW) / halfW) if halfW > 0 else 0
        rightEdge = vTipX + vWidth * (1 - abs(x - halfW) / halfW) if halfW > 0 else screenW
        return leftEdge <= x <= rightEdge

    def fireMeatball(self, bx=None, player=None):
        if bx is None:
            margin = int(const.scaleValue(60, self.screen[0], self.screen[1]))
            bx     = random.randint(margin, self.enemy.screenW - margin)
        if player is None:
            player = self.player
        by     = -20
        tx     = player.rect.centerx + random.randint(-30, 30)
        ty     = player.rect.centery + random.randint(-30, 30)
        self.bullets.add(
            bullet(
                bx, by, tx, ty,
                screen       = self.screen, difficulty=self.difficulty,
                crossingTime = 0.8, size=(22, 22), color=(120, 60, 180),
                damage       = self.enemy.atk * 2, owner="enemy",
            )
        )

    def startRainFire(self):
        self.data = {
            "timer":          3.5,
            "rainTimer":      0.0,
            "rainInterval":   0.05,
            "bouncyTimer":    0.0,
            "bouncyInterval": 0.5,
        }

    def updateRainFire(self, dt, player, ex, ey):
        d = self.data
        d["timer"] -= dt
        d["rainTimer"] -= dt
        if d["rainTimer"] <= 0:
            self.rainBulletGroup(player)
            d["rainTimer"] = d["rainInterval"]
        d["bouncyTimer"] -= dt
        if d["bouncyTimer"] <= 0:
            for _ in range(5):
                bx = random.randint(50, self.enemy.screenW - 50)
                by = -10 - random.randint(0, 30)
                self.addBulletAtAngle(bx, by, math.radians(90), speed=random.uniform(0.4, 0.5), size=(8, 8), color=(200, 100, 255), bounces=1, ignoreWalls=True)
            d["bouncyTimer"] = d["bouncyInterval"]
        if d["timer"] <= 0:
            self.endState()

    def rainBulletGroup(self, player, countRange=(10, 14)):
        margin = int(const.scaleValue(60, self.screen[0], self.screen[1]))
        cx     = random.randint(margin, self.enemy.screenW - margin)
        count  = random.randint(*countRange)
        for i in range(count):
            ox = cx + random.randint(-80, 80)
            oy = -10 - random.randint(0, 30)
            tx = ox + random.randint(-20, 20)
            ty = self.enemy.screenH + 20
            self.bullets.add(
                bullet(
                    ox, oy, tx, ty,
                    screen       = self.screen, difficulty=self.difficulty,
                    crossingTime = 0.75, size=(7, 7), color=(180, 100, 255),
                    damage       = self.enemy.atk, owner="enemy",
                    ignoreWalls  = True,
                )
            )


    def startEye(self):
        ex, ey = self.enemy.rect.center
        target    = pygame.Vector2(self.player.rect.center) if hasattr(self, "player") and self.player is not None else pygame.Vector2(ex + 100, ey)
        self.data = {
            "timer":       1.35,
            "fireTimer":   0.22,
            "phaseState":  "telegraph",
            "angle":       self.aimAngle((ex, ey), target),
        }
        self.sniperBeam       = ((ex, ey), self.data["angle"])
        self.sniperBeamActive = False

    def updateEye(self, dt, player, ex, ey):
        d = self.data

        if d["phaseState"] == "telegraph":
            targetAngle = self.aimAngle((ex, ey), player.rect.center)
            diff        = math.atan2(math.sin(targetAngle - d["angle"]), math.cos(targetAngle - d["angle"]))
            aimSpeed    = {1: 0.07, 2: 0.1, 3: 0.14}.get(self.phase, 0.07)
            d["angle"] += diff * aimSpeed
            self.sniperBeam = ((ex, ey), d["angle"])
            d["timer"] -= dt
            if d["timer"] <= 0:
                d["phaseState"] = "fire"
                self.sniperBeamActive = True

        elif d["phaseState"] == "fire":
            self.sniperBeam = ((ex, ey), d["angle"])
            d["fireTimer"] -= dt
            if d["fireTimer"] <= 0:
                self.endState()

    def startBrick(self):
        start      = pygame.Vector2(self.enemy.rect.center)
        scaledRect = const.scaleSize((92, 62), self.screen[0], self.screen[1])
        self.data  = {
            "timer":       4.5,
            "pos":         start,
            "rect":        pygame.Rect(0, 0, scaledRect[0], scaledRect[1]),
            "velocity":    pygame.Vector2(0, 0),
            "state":       "aim",
            "pauseTimer":  0.0,
            "burstsFired": 0,
            "burstTotal":  4 if self.phase == 1 else (6 if self.phase == 2 else 8),
        }
        self.data["rect"].center = start

    def updateBrick(self, dt, player, ex, ey):
        self.data["timer"] -= dt

        if self.data["state"] == "aim":
            target    = pygame.Vector2(player.rect.center)
            direction = target - self.data["pos"]
            if direction.length() == 0:
                direction   = pygame.Vector2(1, 0)
            speedFactor = const.getScreenScaleFactor(self.screen[0], self.screen[1])
            self.data["velocity"] = direction.normalize() * (680 * speedFactor)
            self.addWarnedSpawn([(int(self.data["pos"].x), int(self.data["pos"].y))], lambda: self.spawnAftonCircle(), 0.35)
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

        if self.data["state"] == "dash":
            if self.data["rect"].colliderect(player.rect):
                player.takeDamage(max(1, player.maxHp // 2))
            if hitWall:
                if self.data["burstsFired"] >= self.data["burstTotal"]:
                    self.endState()
                    return
                self.data["velocity"] = pygame.Vector2(0, 0)
                self.data["pauseTimer"] = 0.18
                self.data["state"] = "pause"

        if self.data["state"] == "pause":
            self.data["pauseTimer"] -= dt
            if self.data["pauseTimer"] <= 0:
                self.data["state"] = "aim"

        if self.data["timer"] <= 0:
            self.endState()

    def spawnAftonCircle(self):
        x, y = self.data["pos"]
        count = 18 if self.phase == 1 else 24
        for i in range(count):
            angle = math.tau * i / count
            self.addBulletAtAngle(x, y, angle, speed=0.6, size=(12, 12), color=(145, 0, 210))

    def startCalamitas(self):
        spots           = 9 if self.phase == 1 else 14
        margin          = int(const.scaleValue(90, self.screen[0], self.screen[1]))
        self.warnPoints = [
            (random.randint(margin, self.enemy.screenW - margin), random.randint(margin, self.enemy.screenH - margin))
            for _ in range(spots)
        ]
        self.data = {"timer": 0.9, "fired": False}

    def updateCalamitas(self, dt, player, ex, ey):
        self.data["timer"] -= dt
        if self.data["timer"] <= 0 and not self.data["fired"]:
            for idx, (x, y) in enumerate(self.warnPoints):
                if idx % 3 == 0:
                    base = self.aimAngle((x, y), player.rect.center) if self.phase >= 2 else random.uniform(0, math.tau)
                    for offset in (-32, -16, 0, 16, 32):
                        self.addBulletAtAngle(x, y, base + math.radians(offset), speed=0.67, size=(9, 9), color=(255, 125, 0))
                else:
                    angle = self.aimAngle((x, y), player.rect.center) if self.phase >= 2 else random.uniform(0, math.tau)
                    self.addBulletAtAngle(x, y, angle, speed=0.68, size=(9, 9), color=(255, 125, 0))
            self.data["fired"] = True
            self.endState()

    def startPyramid(self):
        self.data = {"timer": 1.4, "shotTimer": 0.0, "lagTarget": pygame.Vector2(self.player.rect.center) if hasattr(self, "player") and self.player is not None else pygame.Vector2(0, 0)}

    def updatePyramid(self, dt, player, ex, ey):
        self.data["timer"] -= dt
        self.data["shotTimer"] -= dt
        if self.data["shotTimer"] <= 0:
            base  = self.aimAngle((ex, ey), player.rect.center)
            speed = {1: 460, 2: 520, 3: 580}.get(self.phase, 460) * self.difficulty
            for offset in (-10, 0, 10):
                self.bullets.add(
                    triangleShot(
                        ex, ey,
                        base + math.radians(offset),
                        speed,
                        self.enemy.atk,
                        self.screen,
                        shootsEyes = self.phase >= 2,
                        target     = pygame.Vector2(self.data["lagTarget"]),
                    )
                )
            if self.phase >= 2:
                self.data["lagTarget"] = pygame.Vector2(player.rect.center)
            self.data["shotTimer"] = 0.33

        for tri in [b for b in self.bullets if isinstance(b, triangleShot) and b.shootsEyes and b.eyeTimer <= 0]:
            target = tri.target if tri.target is not None else pygame.Vector2(player.rect.center)
            self.bullets.add(
                delayedAimBullet(
                    tri.rect.centerx, tri.rect.centery, target.x, target.y,
                    screen       = self.screen,
                    difficulty   = self.difficulty,
                    delay        = 0.22,
                    crossingTime = 0.58,
                    size         = (24, 16),
                    color        = (255, 55, 55),
                    damage       = self.enemy.atk,
                    owner        = "enemy",
                )
            )
            tri.eyeTimer = 1

        if self.data["timer"] <= 0:
            self.endState()


    def startBeamDance(self):
        self.warnPoints = []
        laserCount      = 4 + (1 if self.phase >= 2 else 0)
        self.lasers     = []
        for _ in range(laserCount):
            sx          = random.randint(0, self.enemy.screenW)
            sy          = random.randint(0, self.enemy.screenH)
            tx          = random.randint(0, self.enemy.screenW)
            ty          = random.randint(0, self.enemy.screenH)
            angle       = self.aimAngle((sx, sy), (tx, ty))
            mvx         = random.uniform(-80, 80)
            mvy         = random.uniform(-80, 80)
            targetAngle = self.aimAngle((sx, sy), self.player.rect.center) if self.phase >= 2 else angle
            self.lasers.append({"pos": [sx, sy], "angle": angle, "move": (mvx, mvy), "target": targetAngle})
        tele      = 0.8
        hold      = 0.5
        fire      = 1.2 if self.phase == 1 else 1.6
        reload    = 0.6
        self.data = {
            "timer":      3.5 if self.phase == 1 else 4.5,
            "stage":      "tele",
            "stageTimer": tele,
            "tele":       tele,
            "hold":       hold,
            "fire":       fire,
            "reload":     reload,
            "fireRate":   0.22,
            "fireClock":  0.0,
            "aimSpeed":   0.6,
        }

    def updateBeamDance(self, dt, player, ex, ey):
        d = self.data
        d["timer"] -= dt
        d["stageTimer"] -= dt
        newLasers = []
        for laser in self.lasers:
            sx, sy         = laser["pos"]
            mvx, mvy       = laser["move"]
            sx            += mvx * dt
            sy            += mvy * dt
            angle          = laser["angle"]
            targetAngle    = laser.get("target", angle)
            diff           = math.atan2(math.sin(targetAngle - angle), math.cos(targetAngle - angle))
            aimSpeed       = d.get("aimSpeed", 0.6)
            angle += diff * (aimSpeed * dt)
            laser["pos"]   = [sx, sy]
            laser["angle"] = angle
            newLasers.append(laser)
        self.lasers = newLasers

        if d["stage"] in ("tele", "hold"):
            self.warnPoints = [(int(l["pos"][0]), int(l["pos"][1])) for l in self.lasers]
        else:
            self.warnPoints = []

        if d["stageTimer"] <= 0:
            if d["stage"] == "tele":
                d["stage"] = "hold"
                d["stageTimer"] = d["hold"]
            elif d["stage"] == "hold":
                d["stage"] = "fire"
                d["stageTimer"] = d["fire"]
                d["fireClock"] = 0.0
            elif d["stage"] == "fire":
                d["stage"] = "reload"
                d["stageTimer"] = d["reload"]
            elif d["stage"] == "reload":
                d["stage"] = "tele"
                d["stageTimer"] = d["tele"]

        if d["stage"] == "fire":
            d["fireClock"] -= dt
            if d["fireClock"] <= 0:
                d["fireClock"] = d["fireRate"]
                for laser in self.lasers:
                    x, y = laser["pos"]
                    angle = laser["angle"]
                    for off in (-0.05, 0, 0.05):
                        self.addBulletAtAngle(x, y, angle + off, speed=0.9, size=(8, 8), color=(255, 200, 80))
                eyeShots = 1 if self.phase == 1 else (2 if self.phase == 2 else 4)
                for _ in range(eyeShots):
                    spread = random.uniform(-0.14, 0.14)
                    self.addBulletAtAngle(ex, ey, self.aimAngle((ex, ey), player.rect.center) + spread, speed=0.5, size=(9, 9), color=(255, 220, 90))
                if self.phase >= 2 and random.random() < (0.12 if self.phase >= 3 else 0.08):
                    for laser in self.lasers:
                        sx, sy = laser["pos"]
                        self.addBulletAtAngle(sx, sy, self.aimAngle((sx, sy), player.rect.center), speed=0.6)

        if d["timer"] <= 0:
            self.endState()

    def startPowerOfRah(self):
        center                 = (self.enemy.screenW // 2, self.enemy.screenH // 2)
        self.enemy.rect.center = center
        self.enemy.posX        = float(self.enemy.rect.x)
        self.enemy.posY        = float(self.enemy.rect.y)
        baseAngles             = [0, math.tau / 3, 2 * math.tau / 3]
        self.lasers            = [{"pos": (center[0], center[1]), "angle": a, "move": (0, 0), "target": a} for a in baseAngles]
        self.data              = {
            "timer":         4.5,
            "explodeTimer":  0.6,
            "spinSpeed":     0.12,
            "spinAccel":     0.02,
            "spinMax":       1.0 + 0.2 * self.phase,
            "shotgunTimer":  0.9,
            "minigunTimer":  0.035,
        }

    def updatePowerOfRah(self, dt, player, ex, ey):
        self.data["timer"] -= dt
        self.data["explodeTimer"] -= dt
        self.data["spinSpeed"] = min(self.data["spinMax"], self.data["spinSpeed"] + self.data["spinAccel"] * dt)
        ex, ey = self.enemy.rect.center
        newLasers = []
        for laser in self.lasers:
            angle = laser["angle"] + self.data["spinSpeed"] * dt
            laser["angle"] = angle
            newLasers.append(laser)
        self.lasers = newLasers

        if self.data["explodeTimer"] <= 0:
            self.addWarnedSpawn([(ex, ey)], lambda ex=ex, ey=ey: self.bullets.add(
                explodingBullet(
                    ex, ey,
                    self.player.rect.centerx, self.player.rect.centery,
                    screen       = self.screen,
                    difficulty   = self.difficulty,
                    crossingTime = 0.55,
                    size         = (18, 18),
                    color        = (255, 180, 40),
                    damage       = self.enemy.atk,
                    owner        = "enemy",
                    childCount   = 20,
                    childColor   = (255, 200, 80),
                )
            ), 0.35)
            self.data["explodeTimer"] = 0.5 if self.phase == 1 else 0.35

        if self.phase >= 2:
            self.data["shotgunTimer"] -= dt
            if self.data["shotgunTimer"] <= 0:
                self.data["shotgunTimer"] = 0.9
                self.addWarnedSpawn([(ex, ey)], lambda ex=ex, ey=ey: [self.addBulletAtAngle(ex, ey, self.aimAngle((ex, ey), self.player.rect.center) + a, speed=0.5, size=(9, 9), color=(255, 160, 50)) for a in (-0.18, -0.09, 0, 0.09, 0.18)], 0.35)

        if self.phase >= 3:
            self.data["minigunTimer"] -= dt
            if self.data["minigunTimer"] <= 0:
                self.data["minigunTimer"] = 0.035
                self.addBulletAtAngle(ex, ey, self.aimAngle((ex, ey), player.rect.center), speed=0.38, size=(6, 6), color=(255, 240, 120))

        if self.data["timer"] <= 0:
            self.endState()

    def startWallsOfRah(self):
        self.enemy.rect.center = (int(self.enemy.screenW * 0.85), self.enemy.screenH // 2)
        self.enemy.posX        = float(self.enemy.rect.x)
        self.enemy.posY        = float(self.enemy.rect.y)
        wallCount              = 3 + (self.phase - 1)
        self.data              = {
            "wallsLeft":  wallCount,
            "pauseTimer": 0.9,
            "firing":     False,
        }

    def prFireWallsOfRah(self, wx, gapStart, gapEnd):
        spacing = max(55, int(const.scaleValue(55, self.screen[0], self.screen[1])))
        for y in range(0, self.enemy.screenH, spacing):
            if gapStart <= y <= gapEnd:
                continue
            base   = self.aimAngle((wx, y), self.player.rect.center)
            spread = 0.12
            for a in (-spread, 0, spread):
                self.addBulletAtAngle(wx, y, base + a, speed=0.55, size=(8, 8), color=(255, 180, 60))

    def updateWallsOfRah(self, dt, player, ex, ey):
        d = self.data
        if d["wallsLeft"] <= 0:
            self.endState()
            return

        d["pauseTimer"] -= dt
        if d["pauseTimer"] > 0:
            return

        gapSize       = max(160, int(const.scaleValue(200, self.screen[0], self.screen[1])))
        gapStart      = random.randint(gapSize, self.enemy.screenH - gapSize * 2)
        spacing       = max(55, int(const.scaleValue(55, self.screen[0], self.screen[1])))
        wx            = random.randint(int(self.enemy.screenW * 0.1), int(self.enemy.screenW * 0.85))
        warnPositions = [(wx, y) for y in range(0, self.enemy.screenH, spacing) if not (gapStart <= y <= gapStart + gapSize)]
        self.addWarnedSpawn(warnPositions, lambda wx=wx: self.prFireWallsOfRah(wx, gapStart, gapSize + gapSize), 0.35)

        d["wallsLeft"] -= 1
        d["pauseTimer"] = 1.1 if self.phase == 1 else (0.85 if self.phase == 2 else 0.65)

    def startLanceOfRah(self):
        ex, ey = self.enemy.rect.center
        for angle in (0, math.pi / 2, math.pi, 3 * math.pi / 2):
            lance = lanceProjectile(ex, ey, angle, self.screen, self.difficulty, self.enemy.atk, self.bullets, self.player, self.phase)
            self.bullets.add(lance)
        self.data = {"timer": 4.0}

    def updateLanceOfRah(self, dt, player, ex, ey):
        self.data["timer"] -= dt
        if self.data["timer"] <= 0:
            self.endState()


    def startSplitter(self):
        self.splitterActive = True
        self.splitterTimer  = 5.0
        beamCount          = {1: 1, 2: 4, 3: 6}.get(self.phase, 1)
        self.splitterBeams = []
        for i in range(beamCount):
            angle = math.tau * i / beamCount + random.uniform(-0.3, 0.3)
            self.splitterBeams.append({"angle": angle, "speed": 0.3})

    def updateSplitter(self, dt, player, ex, ey):
        self.splitterTimer -= dt
        if self.splitterTimer <= 0:
            self.splitterActive = False
            self.splitterBeams  = []
            return
        for beam in self.splitterBeams:
            beam["angle"] += beam["speed"] * dt


    def startDesperation(self):
        self.desperation       = True
        self.desperationTimer  = self.desperationDuration
        self.desperationStage  = 0
        self.state             = None
        self.queue.clear()
        self.spinners          = []
        self.lasers            = []
        self.beamSpinners      = []
        self.bullets.empty()
        self.eyeLaser          = None
        self.pendingWarns      = []
        self.deactivateShields()
        self.splitterActive    = False
        self.splitterBeams     = []
        self.enemy.rect.center = (self.enemy.screenW // 2, self.enemy.screenH // 2)
        self.enemy.posX        = float(self.enemy.rect.x)
        self.enemy.posY        = float(self.enemy.rect.y)
        self.desperationData   = {
            "circleTimer":        0.0,
            "circleInterval":     0.6,
            "rainTimer":          0.0,
            "rainInterval":       0.2,
            "beamSpinners":       [],
            "bulletHellTimer":    0.0,
            "bulletHellInterval": 0.3,
        }

    def updateDesperation(self, dt, player, ex, ey):
        self.desperationTimer -= dt
        d       = self.desperationData
        elapsed = self.desperationDuration - self.desperationTimer

        if elapsed < 15:
            self.desperationStage = 0
            d["circleTimer"] -= dt
            if d["circleTimer"] <= 0:
                px, py     = player.rect.center
                count      = 10
                radius     = int(const.scaleValue(160, self.screen[0], self.screen[1]))
                for i in range(count):
                    angle  = math.tau * i / count
                    bx     = px + math.cos(angle) * radius
                    by     = py + math.sin(angle) * radius
                    inward = self.aimAngle((bx, by), player.rect.center)
                    self.addBulletAtAngle(bx, by, inward, speed=0.45, size=(8, 8), color=(255, 80, 80))
                d["circleTimer"] = d["circleInterval"]
            d["rainTimer"] -= dt
            if d["rainTimer"] <= 0:
                self.rainBulletGroup(player, countRange=(14, 20))
                d["rainTimer"] = d["rainInterval"]

        elif elapsed < 30:
            self.desperationStage = 1
            if not d["beamSpinners"]:
                cx, cy = self.enemy.rect.center
                length = max(self.enemy.screenW, self.enemy.screenH)
                d["beamSpinners"] = [
                    beamSpinner(cx, cy, 0, math.radians(10), length),
                    beamSpinner(cx, cy, math.pi / 2, math.radians(-10), length),
                ]
            d["rainTimer"] -= dt
            if d["rainTimer"] <= 0:
                self.rainBulletGroup(player, countRange=(14, 20))
                d["rainTimer"] = d["rainInterval"]
            for bs in d["beamSpinners"]:
                bs.update(dt)

        elif elapsed < 60:
            self.desperationStage = 2
            d["beamSpinners"] = []
            d["bulletHellTimer"] -= dt
            if d["bulletHellTimer"] <= 0:
                positions = [(random.randint(50, self.enemy.screenW - 50),
                              random.randint(50, self.enemy.screenH - 50))
                             for _ in range(4)]
                self.addWarnedSpawn(positions, lambda p=positions: self.spawnWarnedBullets({"pendingPositions": p}), 0.3)
                d["bulletHellTimer"] = d["bulletHellInterval"]
            d["rainTimer"] -= dt
            if d["rainTimer"] <= 0:
                self.rainBulletGroup(player, countRange=(14, 20))
                d["rainTimer"] = d["rainInterval"]

        if self.desperationTimer <= 0:
            self.enemy.hp = 0
            self.enemy.kill()

    def beamHitsPlayer(self, player):
        if self.desperation and self.desperationStage == 1:
            d         = self.desperationData
            threshold = const.scaleValue(10, self.screen[0], self.screen[1])
            for bs in d.get("beamSpinners", []):
                (ex, ey), (ox, oy) = bs.getEndpoints()
                if self.distanceToLine(player.rect.center, (ex, ey), (ox, oy)) <= threshold:
                    return True
        if self.state == "summonSpinner":
            threshold = const.scaleValue(8, self.screen[0], self.screen[1])
            for bs in self.beamSpinners:
                (ex, ey), (ox, oy) = bs.getEndpoints()
                if self.distanceToLine(player.rect.center, (ex, ey), (ox, oy)) <= threshold:
                    return True
        if self.sniperBeamActive and self.sniperBeam is not None:
            threshold = const.scaleValue(11, self.screen[0], self.screen[1])
            start, angle = self.sniperBeam
            px, py = player.rect.center
            sx, sy = start
            dx, dy = math.cos(angle), math.sin(angle)
            dist = abs((px - sx) * dy - (py - sy) * dx)
            if dist <= threshold:
                return True
        if self.lasers:
            threshold = int(const.scaleValue(12, self.screen[0], self.screen[1]))
            for laser in self.lasers:
                start = laser.get("pos")
                angle = laser.get("angle")
                px, py = player.rect.center
                sx, sy = start
                dx, dy = math.cos(angle), math.sin(angle)
                dist = abs((px - sx) * dy - (py - sy) * dx)
                if dist <= threshold:
                    return True
        if self.splitterActive:
            ex, ey = self.enemy.rect.center
            threshold = int(const.scaleValue(8, self.screen[0], self.screen[1]))
            for beam in self.splitterBeams:
                a      = beam["angle"]
                length = max(self.enemy.screenW, self.enemy.screenH)
                endX   = ex + math.cos(a) * length
                endY   = ey + math.sin(a) * length
                oX     = ex - math.cos(a) * length
                oY     = ey - math.sin(a) * length
                if self.distanceToLine(player.rect.center, (endX, endY), (oX, oY)) <= threshold:
                    return True
        return False

    def distanceToLine(self, point, a, b):
        px, py = point
        ax, ay = a
        bx, by = b
        dx, dy = bx - ax, by - ay
        lengthSq = dx * dx + dy * dy
        if lengthSq == 0:
            return math.hypot(px - ax, py - ay)
        t     = max(0, min(1, ((px - ax) * dx + (py - ay) * dy) / lengthSq))
        projX = ax + t * dx
        projY = ay + t * dy
        return math.hypot(px - projX, py - projY)

    def draw(self, screen):
        self.bullets.draw(screen)

        if self.warnPoints:
            surf       = pygame.Surface((self.enemy.screenW, self.enemy.screenH), pygame.SRCALPHA)
            warnRadius = int(const.scaleValue(16, self.screen[0], self.screen[1]))
            warnWidth  = max(1, int(const.scaleValue(3, self.screen[0], self.screen[1])))
            for x, y in self.warnPoints:
                pygame.draw.circle(surf, (*const.blue[:3], 160), (x, y), warnRadius, warnWidth)
            screen.blit(surf, (0, 0))

        if self.warnDirLines:
            surf = pygame.Surface((self.enemy.screenW, self.enemy.screenH), pygame.SRCALPHA)
            for start, end in self.warnDirLines:
                pygame.draw.line(surf, (255, 255, 255, 160), start, end, 1)
            screen.blit(surf, (0, 0))

        if self.state == "summonSpinner":
            surf       = pygame.Surface((self.enemy.screenW, self.enemy.screenH), pygame.SRCALPHA)
            laserWidth = max(1, int(const.scaleValue(6, self.screen[0], self.screen[1])))
            for bs in self.beamSpinners:
                (ex, ey), (ox, oy) = bs.getEndpoints()
                pygame.draw.line(surf, (100, 200, 255, 140), (ex, ey), (ox, oy), laserWidth)
            screen.blit(surf, (0, 0))

        if self.desperation and self.desperationStage == 1:
            d          = self.desperationData
            surf       = pygame.Surface((self.enemy.screenW, self.enemy.screenH), pygame.SRCALPHA)
            laserWidth = max(1, int(const.scaleValue(8, self.screen[0], self.screen[1])))
            for bs in d.get("beamSpinners", []):
                (ex, ey), (ox, oy) = bs.getEndpoints()
                pygame.draw.line(surf, (255, 50, 50, 160), (ex, ey), (ox, oy), laserWidth)
            screen.blit(surf, (0, 0))

        if self.sniperBeam is not None:
            start, angle = self.sniperBeam
            end       = (start[0] + math.cos(angle) * 3000, start[1] + math.sin(angle) * 3000)
            color     = (255, 0, 0, 220) if self.sniperBeamActive else (255, 40, 40, 90)
            beamWidth = int(const.scaleValue(9 if self.sniperBeamActive else 3, self.screen[0], self.screen[1]))
            beamWidth = max(1, beamWidth)
            pygame.draw.line(screen, color, start, end, beamWidth)

        if self.lasers and self.state in ("beamDance", "powerOfRah"):
            surf      = pygame.Surface((self.enemy.screenW, self.enemy.screenH), pygame.SRCALPHA)
            beamWidth = max(1, int(const.scaleValue(4, self.screen[0], self.screen[1])))
            color     = (255, 200, 40, 140)
            for laser in self.lasers:
                start = laser["pos"]
                angle = laser["angle"]
                end   = (start[0] + math.cos(angle) * 3000, start[1] + math.sin(angle) * 3000)
                pygame.draw.line(surf, color, start, end, beamWidth)
            screen.blit(surf, (0, 0))

        if self.state == "brick" and self.data:
            x, y = self.data["pos"]
            brickSize = const.scaleSize((76, 52), self.screen[0], self.screen[1])
            pygame.draw.rect(screen, (120, 0, 170), pygame.Rect(x - brickSize[0] // 2, y - brickSize[1] // 2, brickSize[0], brickSize[1]))

        if self.phase == 2 and self.shieldActive:
            for shield in self.shields:
                if hasattr(shield, "x"):
                    pygame.draw.circle(screen, const.cyan, (int(shield.x), int(shield.y)), 28)

        if self.splitterActive:
            surf = pygame.Surface((self.enemy.screenW, self.enemy.screenH), pygame.SRCALPHA)
            ex, ey = self.enemy.rect.center
            beamWidth = max(1, int(const.scaleValue(6, self.screen[0], self.screen[1])))
            progress  = 1.0 - (self.splitterTimer / 5.0)
            alpha     = min(255, int(120 + progress * 100))
            color     = (255, 60, 60, alpha)
            for beam in self.splitterBeams:
                a    = beam["angle"]
                endX = ex + math.cos(a) * max(self.enemy.screenW, self.enemy.screenH) * 1.5
                endY = ey + math.sin(a) * max(self.enemy.screenW, self.enemy.screenH) * 1.5
                oX   = ex - math.cos(a) * max(self.enemy.screenW, self.enemy.screenH) * 1.5
                oY   = ey - math.sin(a) * max(self.enemy.screenW, self.enemy.screenH) * 1.5
                pygame.draw.line(surf, color, (oX, oY), (endX, endY), beamWidth)
            screen.blit(surf, (0, 0))
