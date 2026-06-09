import math
import random
import pygame
import const
from entity.weapons.bullet import bullet
from mapping.maps import getWallRects, getBreakableRectsWithCoords, breakTile

class explodingBullet(bullet):
    def __init__(self, *args, childCount=18, childColor=(255, 200, 60), childSize=(8,8), childSpeed=0.55, **kwargs):
        super().__init__(*args, **kwargs)
        self.childCount    = childCount
        self.childColor    = childColor
        self.childSize     = childSize
        self.childSpeed    = childSpeed

    def explode(self, group):
        x, y = self.rect.center
        for i in range(self.childCount):
            angle = math.tau * i / self.childCount
            bounces = 1 if random.random() < 0.1 else 0
            group.add(
                bullet(
                    x, y,
                    x + math.cos(angle) * 1000,
                    y + math.sin(angle) * 1000,
                    screen       = self.screen,
                    difficulty   = self.difficulty if hasattr(self, 'difficulty') else 1.0,
                    crossingTime = self.childSpeed,
                    size         = self.childSize,
                    color        = self.childColor,
                    damage       = self.damage,
                    owner        = "enemy",
                    maxBounces   = bounces,
                )
            )
        self.kill()

class lanceProjectile(pygame.sprite.Sprite):
    def __init__(self, x, y, angle, screen, difficulty, enemyAtk, bulletsGroup, playerRef, phase):
        super().__init__()
        self.pos = pygame.Vector2(x, y)
        self.angle = angle
        self.speed = 420 if phase == 1 else (520 if phase == 2 else 620)
        self.velocity = pygame.Vector2(math.cos(angle), math.sin(angle)) * self.speed
        self.image = pygame.Surface((14, 14), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (255,200,80), (7,7), 7)
        self.rect = self.image.get_rect(center=(x,y))
        self.screen = screen
        self.difficulty = difficulty
        self.atk = enemyAtk
        self.damage = enemyAtk
        self.owner = "enemy"
        self.spawnTimer = 0.0
        self.bulletsGroup = bulletsGroup
        self.playerRef = playerRef
        self.life = 4.0
        self.phase = phase


    def update(self, dt, screenW, screenH, wallRects=None, breakableData=None, onBreak=None):
        self.life -= dt
        self.pos += self.velocity * dt
        self.rect.center = self.pos
        self.spawnTimer -= dt
        if self.spawnTimer <= 0:
            self.spawnTimer = (0.6 if self.phase == 1 else (0.4 if self.phase == 2 else 0.28))
            for a in (0, math.pi/2):
                b = bullet(self.rect.centerx, self.rect.centery,
                           self.rect.centerx + math.cos(a) * 1000,
                           self.rect.centery + math.sin(a) * 1000,
                           screen=self.screen, difficulty=self.difficulty,
                           crossingTime=0.6, size=(9,9), color=(255,150,40), owner="enemy", maxBounces=1, damage=self.atk)
                self.bulletsGroup.add(b)
            if self.playerRef is not None:
                aim = math.atan2(self.playerRef.rect.centery - self.rect.centery, self.playerRef.rect.centerx - self.rect.centerx)
                for _ in range(2 + (1 if self.phase >= 3 else 0)):
                    b = bullet(self.rect.centerx, self.rect.centery,
                               self.rect.centerx + math.cos(aim) * 1000,
                               self.rect.centery + math.sin(aim) * 1000,
                               screen=self.screen, difficulty=self.difficulty,
                               crossingTime=0.6, size=(9,9), color=(255,90,40), owner="enemy")
                    self.bulletsGroup.add(b)

        if (self.rect.right < 0 or self.rect.left > screenW or self.rect.bottom < 0 or self.rect.top > screenH) or self.life <= 0:
            self.kill()
            return
        if wallRects:
            for wall in wallRects:
                if self.rect.colliderect(wall):
                    self.kill()
                    return

class bossFiveAIClass:
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
        self.lasers              = []
        self.warnPoints          = []
        self.desperation         = False
        self.desperationDuration = 30.0
        self.desperationTimer    = 0.0
        self.moveTarget          = pygame.Vector2(enemy.rect.center)
        self.moveTimer           = 0.0
        self.phaseTwoImage       = None
        self.phaseThreeImage     = None
        self.phaseName           = "Rah"

    def update(self, dt, roomId, player):
        self.player = player

        if not self.desperation and self.enemy.hp <= self.maxHp * 0.05:
            self.startDesperation()
        elif self.phase == 1 and self.enemy.hp <= self.maxHp * 0.66:
            self.phase = 2
        elif self.phase == 2 and self.enemy.hp <= self.maxHp * 0.33:
            self.phase = 3
        print(self.phase)

        match self.phase:
            case 2:
                self.usePhaseTwoImage()
                self.phaseName = "EYE OF RAH"
            case 3:
                self.usePhaseThreeImage()
                self.phaseName = "EYE OF RAH UNLEASHED"

        ex, ey = self.enemy.rect.center

        if not hasattr(self, 'eyeLaser'):
            tele = 0.8
            hold = 0.5
            fire = 1.4
            reload = 0.6
            targetAngle = self.aimAngle((ex, ey), self.player.rect.center)
            self.eyeLaser = {
                'start': (ex, ey),
                'currentAngle': targetAngle,
                'targetAngle': targetAngle,
                'stage': 'tele',
                'stageTimer': tele,
                'tele': tele,
                'hold': hold,
                'fire': fire,
                'reload': reload,
                'aimInterp': 0.7,
                'spawnTimer': 0.0,
                'spawnInterval': 0.9,
            }
        else:
            self.eyeLaser['start'] = (ex, ey)
            self.eyeLaser['targetAngle'] = self.aimAngle((ex, ey), self.player.rect.center)

            aimByPhase = {1: 1, 2: 1.5, 3: 2}
            self.eyeLaser['aimInterp'] = aimByPhase.get(self.phase, 0.7)

            self.eyeLaser['stageTimer'] -= dt
            if self.eyeLaser['stageTimer'] <= 0:
                s = self.eyeLaser['stage']
                if s == 'tele':
                    self.eyeLaser['stage'] = 'hold'
                    self.eyeLaser['stageTimer'] = self.eyeLaser['hold']
                elif s == 'hold':
                    self.eyeLaser['stage'] = 'fire'
                    self.eyeLaser['stageTimer'] = self.eyeLaser['fire']
                    if self.phase == 1:
                        self.eyeLaser['spawnInterval'] = 0.9
                    elif self.phase == 2:
                        self.eyeLaser['spawnInterval'] = 0.6
                    else:
                        self.eyeLaser['spawnInterval'] = 0.4
                    self.eyeLaser['spawnTimer'] = self.eyeLaser['spawnInterval']
                elif s == 'fire':
                    self.eyeLaser['stage'] = 'reload'
                    self.eyeLaser['stageTimer'] = self.eyeLaser['reload']
                elif s == 'reload':
                    self.eyeLaser['stage'] = 'tele'
                    self.eyeLaser['stageTimer'] = self.eyeLaser['tele']

            if self.eyeLaser['stage'] in ('tele', 'hold'):
                cur = self.eyeLaser['currentAngle']
                targ = self.eyeLaser['targetAngle']
                diff = math.atan2(math.sin(targ - cur), math.cos(targ - cur))
                self.eyeLaser['currentAngle'] = cur + diff * (self.eyeLaser['aimInterp'] * dt)

            if self.eyeLaser['stage'] == 'fire':
                self.eyeLaser['spawnTimer'] -= dt
                if self.eyeLaser['spawnTimer'] <= 0:
                    self.eyeLaser['spawnTimer'] = self.eyeLaser['spawnInterval']
                    spawnCount = 1 if self.phase == 1 else (3 if self.phase == 2 else 5)
                    dists = [120, 260, 400, 540, 700]
                    for i in range(min(spawnCount, len(dists))):
                        dist = dists[i]
                        angle = self.eyeLaser['currentAngle']
                        sx = ex + math.cos(angle) * dist
                        sy = ey + math.sin(angle) * dist
                        self.addBulletAtAngle(sx, sy, self.aimAngle((sx, sy), self.player.rect.center), speed=0.6, size=(9,9), color=(255,180,60))
                        if self.phase >= 2:
                            perpA = angle + math.pi/2
                            perpB = angle - math.pi/2
                            self.addBulletAtAngle(sx, sy, perpA, speed=0.7, size=(7,7), color=(255,140,40))
                            self.addBulletAtAngle(sx, sy, perpB, speed=0.7, size=(7,7), color=(255,140,40))

        if self.desperation:
            self.updateDesperation(dt)
        else:
            self.updateMovement(dt, roomId)
            self.updateQueue()
            match self.state:
                case "beamDance": self.updateBeamDance(dt)
                case "powerOfRah": self.updatePowerOfRah(dt)
                case "lanceOfRah": self.updateLanceOfRah(dt)
                case "barrage": self.updateBarrage(dt)
                case "wallsOfRah": self.updateWallsOfRah(dt)
                case "circleShot": self.updateCircleShot(dt)

        wallRects     = getWallRects(roomId, self.enemy.screenW, self.enemy.screenH)
        breakableData = getBreakableRectsWithCoords(roomId, self.enemy.screenW, self.enemy.screenH)

        def onBreak(r, c):
            breakTile(roomId, r, c)

        for b in list(self.bullets):
            if isinstance(b, explodingBullet) and b.rect.colliderect(self.player.rect):
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
        if self.moveTimer <= 0:
            margin = int(const.scaleValue(120, self.screen[0], self.screen[1]))
            self.moveTarget = pygame.Vector2(
                random.randint(margin, self.enemy.screenW - margin),
                random.randint(margin, self.enemy.screenH - margin),
            )
            self.moveTimer = random.uniform(0.8, 1.6)

        self.moveTimer -= dt
        direction = self.moveTarget - pygame.Vector2(self.enemy.rect.center)
        if direction.length() > 5:
            self.enemy.moveAndCollide(direction.normalize() * (260 * dt), roomId)

    def updateQueue(self):
        if self.state is None and not self.queue:
            self.queue = ["beamDance", "powerOfRah", "lanceOfRah", "barrage", "circleShot"]
            if self.phase >= 2:
                self.queue += ["beamDance", "powerOfRah", "lanceOfRah", "barrage", "wallsOfRah"]
            if self.phase >= 3:
                self.queue += ["beamDance","powerOfRah","wallsOfRah", "barrage", "circleShot", "wallsOfRah"]
            random.shuffle(self.queue)

        if self.state is None and self.queue:
            self.state = self.queue.pop(0)
            getattr(self, f"start{self.state[0].upper() + self.state[1:]}")()

    def addBulletAtAngle(self, x, y, angle, speed=0.7, size=(10,10), color=(255,220,60), damage=None, bounces=0):
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

    def startBeamDance(self):
        self.warnPoints = []
        laserCount = 4 + (1 if self.phase >= 2 else 0)
        self.lasers = []
        for _ in range(laserCount):
            sx = random.randint(0, self.enemy.screenW)
            sy = random.randint(0, self.enemy.screenH)
            tx = random.randint(0, self.enemy.screenW)
            ty = random.randint(0, self.enemy.screenH)
            angle = self.aimAngle((sx, sy), (tx, ty))
            mvx = random.uniform(-80, 80)
            mvy = random.uniform(-80, 80)
            targetAngle = self.aimAngle((sx, sy), self.player.rect.center) if self.phase >= 2 else angle
            self.lasers.append({"pos":[sx, sy], "angle":angle, "move":(mvx, mvy), "target": targetAngle})
        tele = 0.8
        hold = 0.5
        fire = 1.2 if self.phase==1 else 1.6
        reload = 0.6
        self.data = {"timer": 3.5 if self.phase==1 else 4.5, "stage":"tele", "stageTimer":tele, "tele":tele, "hold":hold, "fire":fire, "reload":reload, "fireRate":0.22, "fireClock":0.0, "aimSpeed":0.6}

    def updateBeamDance(self, dt):
        d = self.data
        d["timer"] -= dt
        ex, ey = self.enemy.rect.center
        d["stageTimer"] -= dt
        newLasers = []
        for laser in self.lasers:
            sx, sy = laser["pos"]
            mvx, mvy = laser["move"]
            sx += mvx * dt
            sy += mvy * dt
            angle = laser["angle"]
            targetAngle = laser.get("target", angle)
            diff = math.atan2(math.sin(targetAngle - angle), math.cos(targetAngle - angle))
            aimSpeed = d.get("aimSpeed", 0.6)
            angle += diff * (aimSpeed * dt)
            laser["pos"] = [sx, sy]
            laser["angle"] = angle
            newLasers.append(laser)
        self.lasers = newLasers

        if d["stage"] in ("tele", "hold"):
            self.warnPoints = [ (int(l["pos"][0]), int(l["pos"][1])) for l in self.lasers ]
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
                    x,y = laser["pos"]
                    angle = laser["angle"]
                    for off in (-0.05, 0, 0.05):
                        self.addBulletAtAngle(x, y, angle + off, speed=0.9, size=(8,8), color=(255,200,80))
                eyeShots = 1 if self.phase == 1 else (2 if self.phase == 2 else 4)
                for _ in range(eyeShots):
                    spread = random.uniform(-0.14, 0.14)
                    self.addBulletAtAngle(ex, ey, self.aimAngle((ex,ey), self.player.rect.center) + spread, speed=0.5, size=(9,9), color=(255,220,90))
                if self.phase >= 2 and random.random() < (0.12 if self.phase>=3 else 0.08):
                    for laser in self.lasers:
                        sx, sy = laser["pos"]
                        self.addBulletAtAngle(sx, sy, self.aimAngle((sx,sy), self.player.rect.center), speed=0.6)

        if d["timer"] <= 0:
            self.endState()

    def startPowerOfRah(self):
        center = (self.enemy.screenW // 2, self.enemy.screenH // 2)
        self.enemy.rect.center = center
        self.enemy.posX = float(self.enemy.rect.x)
        self.enemy.posY = float(self.enemy.rect.y)
        baseAngles = [0, math.tau/3, 2*math.tau/3]
        self.lasers = [{"pos":(center[0], center[1]), "angle":a, "move":(0,0), "target":a} for a in baseAngles]
        self.data = {
            "timer": 4.5,
            "explodeTimer": 0.6,
            "spinSpeed": 0.12,
            "spinAccel": 0.02,
            "spinMax": 1.0 + 0.2 * self.phase,
            "shotgunTimer": 0.9,
            "minigunTimer": 0.035,
        }

    def updatePowerOfRah(self, dt):
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
            self.bullets.add(
                explodingBullet(
                    ex, ey,
                    self.player.rect.centerx, self.player.rect.centery,
                    screen       = self.screen,
                    difficulty   = self.difficulty,
                    crossingTime = 0.55,
                    size         = (18,18),
                    color        = (255, 180, 40),
                    damage       = self.enemy.atk,
                    owner        = "enemy",
                    childCount   = 20,
                    childColor   = (255,200,80),
                )
            )
            self.data["explodeTimer"] = 0.5 if self.phase==1 else 0.35

        if self.phase >= 2:
            self.data["shotgunTimer"] -= dt
            if self.data["shotgunTimer"] <= 0:
                self.data["shotgunTimer"] = 0.9
                base = self.aimAngle((ex, ey), self.player.rect.center)
                for a in (-0.18, -0.09, 0, 0.09, 0.18):
                    self.addBulletAtAngle(ex, ey, base + a, speed=0.5, size=(9,9), color=(255,160,50))

        if self.phase >= 3:
            self.data["minigunTimer"] -= dt
            if self.data["minigunTimer"] <= 0:
                self.data["minigunTimer"] = 0.035
                self.addBulletAtAngle(ex, ey, self.aimAngle((ex, ey), self.player.rect.center), speed=0.38, size=(6,6), color=(255,240,120))

        if self.data["timer"] <= 0:
            self.endState()

    def startLanceOfRah(self):
        ex, ey = self.enemy.rect.center
        for angle in (0, math.pi/2, math.pi, 3*math.pi/2):
            lance = lanceProjectile(ex, ey, angle, self.screen, self.difficulty, self.enemy.atk, self.bullets, self.player, self.phase)
            self.bullets.add(lance)
        self.data = {"timer": 4.0}

    def updateLanceOfRah(self, dt):
        self.data["timer"] -= dt
        if self.data["timer"] <= 0:
            self.endState()

    def startBarrage(self):
        self.data = {"timer": 3.5, "spawnTimer": 0.55}

    def updateBarrage(self, dt):
        self.data["timer"] -= dt
        self.data["spawnTimer"] -= dt
        if self.data["spawnTimer"] <= 0:
            self.data["spawnTimer"] = 0.55 if self.phase == 1 else (0.42 if self.phase == 2 else 0.32)
            spacing = max(90, int(const.scaleValue(90, self.screen[0], self.screen[1])))
            gapCenter = random.randint(spacing * 2, self.enemy.screenW - spacing * 2)
            gapHalf = int(spacing * 1.8)
            for cx in range(spacing // 2, self.enemy.screenW, spacing):
                if abs(cx - gapCenter) < gapHalf:
                    continue
                rx = cx + random.randint(-spacing // 5, spacing // 5)
                self.bullets.add(
                    bullet(
                        rx, 6,
                        rx + random.uniform(-15, 15), self.enemy.screenH,
                        screen       = self.screen,
                        difficulty   = self.difficulty,
                        crossingTime = 1.0 - (0.1 * self.phase),
                        size         = (8,8),
                        color        = (255,220,60),
                        damage       = self.enemy.atk,
                        owner        = "enemy",
                        ignoreWalls  = True,
                    )
                )

        if self.data["timer"] <= 0:
            self.endState()

    def startWallsOfRah(self):
        self.enemy.rect.center = (int(self.enemy.screenW * 0.85), self.enemy.screenH // 2)
        self.enemy.posX = float(self.enemy.rect.x)
        self.enemy.posY = float(self.enemy.rect.y)
        wallCount = 3 + (self.phase - 1)
        self.data = {
            "wallsLeft": wallCount,
            "pauseTimer": 0.9,
            "firing": False,
        }

    def updateWallsOfRah(self, dt):
        d = self.data
        if d["wallsLeft"] <= 0:
            self.endState()
            return

        d["pauseTimer"] -= dt
        if d["pauseTimer"] > 0:
            return

        gapSize = max(160, int(const.scaleValue(200, self.screen[0], self.screen[1])))
        gapStart = random.randint(gapSize, self.enemy.screenH - gapSize * 2)
        spacing = max(55, int(const.scaleValue(55, self.screen[0], self.screen[1])))
        wx = random.randint(int(self.enemy.screenW * 0.1), int(self.enemy.screenW * 0.85))
        for y in range(0, self.enemy.screenH, spacing):
            if gapStart <= y <= gapStart + gapSize:
                continue
            base = self.aimAngle((wx, y), self.player.rect.center)
            spread = 0.12
            for a in (-spread, 0, spread):
                self.addBulletAtAngle(wx, y, base + a, speed=0.55, size=(8,8), color=(255,180,60))

        d["wallsLeft"] -= 1
        d["pauseTimer"] = 1.1 if self.phase == 1 else (0.85 if self.phase == 2 else 0.65)

    def startCircleShot(self):
        self.data = {"timer": 3.0, "holdTimer": 0.5}
        self.circles = []
        px, py = self.player.rect.center
        count = 18 if self.phase==1 else 26
        radius = int(const.scaleValue(160, self.screen[0], self.screen[1]))
        for i in range(count):
            angle = math.tau * i / count
            sx = px + math.cos(angle) * radius
            sy = py + math.sin(angle) * radius
            b = bullet(sx, sy, sx, sy, screen=self.screen, difficulty=self.difficulty, crossingTime=1000, size=(9,9), color=(255,210,80), damage=self.enemy.atk, owner="enemy")
            b.velocity = pygame.Vector2(0,0)
            self.bullets.add(b)
            self.circles.append(b)

    def updateCircleShot(self, dt):
        self.data["timer"] -= dt
        self.data["holdTimer"] -= dt
        if self.data["holdTimer"] <= 0 and self.circles:
            px, py = self.player.rect.center
            for b in list(self.circles):
                if not b.alive():
                    self.circles.remove(b)
                    continue
                dirv = pygame.Vector2(px - b.rect.centerx, py - b.rect.centery)
                if dirv.length() == 0:
                    dirv = pygame.Vector2(1,0)
                dirv = dirv.normalize() * (0.9 * self.screen[0]) * (1.0 if self.phase==1 else 1.3)
                b.velocity = dirv
            self.circles = []

        if self.data["timer"] <= 0:
            self.endState()

    def startDesperation(self):
        self.desperation = True
        self.desperationTimer = self.desperationDuration
        self.enemy.rect.center = (self.enemy.screenW // 2, self.enemy.screenH // 2)
        self.enemy.posX = float(self.enemy.rect.x)
        self.enemy.posY = float(self.enemy.rect.y)
        self.data = {"splitterAngle": 0.0, "splitterTimer": 0.0, "minigunTimer": 0.02, "shotgunTimer": 0.8, "rainTimer": 0.25}

    def updateDesperation(self, dt):
        self.desperationTimer -= dt
        ex, ey = self.enemy.rect.center
        t = self.desperationTimer
        if t > 20:
            self.data["splitterAngle"] += dt * 0.5
            self.data["splitterTimer"] -= dt
            if self.data["splitterTimer"] <= 0:
                self.data["splitterTimer"] = 0.55
                angle = self.data["splitterAngle"]
                spokeAngles = [angle + (math.tau * i / 3) for i in range(3)]
                for spokeAngle in spokeAngles:
                    minR = 220
                    maxR = min(self.enemy.screenW, self.enemy.screenH) // 2 + 80
                    for r in range(minR, maxR, 200):
                        sx = self.enemy.screenW//2 + math.cos(spokeAngle) * r
                        sy = self.enemy.screenH//2 + math.sin(spokeAngle) * r
                        self.addBulletAtAngle(sx, sy, spokeAngle, speed=0.45, size=(16,16), color=(255,140,40))
        elif 10 < t <= 20:
            self.data["rainTimer"] -= dt
            if self.data["rainTimer"] <= 0:
                self.data["rainTimer"] = 0.7
                spacing = max(90, int(const.scaleValue(90, self.screen[0], self.screen[1])))
                gapCenter = random.randint(spacing * 2, self.enemy.screenW - spacing * 2)
                gapHalf = int(spacing * 2.2)
                for cx in range(spacing // 2, self.enemy.screenW, spacing):
                    if abs(cx - gapCenter) < gapHalf:
                        continue
                    rx = cx + random.randint(-spacing // 5, spacing // 5)
                    self.bullets.add(
                        bullet(
                            rx, 6,
                            rx + random.uniform(-15, 15), self.enemy.screenH,
                            screen       = self.screen,
                            difficulty   = self.difficulty,
                            crossingTime = 0.75,
                            size         = (10,10),
                            color        = (255,220,70),
                            damage       = self.enemy.atk,
                            owner        = "enemy",
                            ignoreWalls  = True,
                        )
                    )
                base = self.aimAngle((ex, ey), self.player.rect.center)
                for a in (-0.18, -0.09, 0, 0.09, 0.18):
                    self.addBulletAtAngle(ex, ey, base + a, speed=0.55, size=(9,9), color=(255,160,80))
        else:
            self.data["minigunTimer"] -= dt
            if self.data["minigunTimer"] <= 0:
                self.data["minigunTimer"] = 0.03
                self.addBulletAtAngle(ex, ey, self.aimAngle((ex,ey), self.player.rect.center), speed=0.35, size=(6,6), color=(255,240,120))
            self.data["shotgunTimer"] -= dt
            if self.data["shotgunTimer"] <= 0:
                self.data["shotgunTimer"] = 0.8
                base = self.aimAngle((ex,ey), self.player.rect.center)
                for a in (-0.18, -0.09, 0, 0.09, 0.18):
                    self.addBulletAtAngle(ex, ey, base + a, speed=0.5, size=(8,8), bounces=1)

        if self.desperationTimer <= 0:
            self.enemy.hp = 0
            self.enemy.kill()

    def beamHitsPlayer(self, player):
        threshold = int(const.scaleValue(12, self.screen[0], self.screen[1]))
        for laser in self.lasers:
            start = laser.get("pos")
            angle = laser.get("angle")
            if self.distanceToBeam(player.rect.center, start, angle) <= threshold:
                return True
        if getattr(self, 'eyeLaser', None) is not None and self.eyeLaser.get('stage') == 'fire':
            start = self.eyeLaser['start']
            angle = self.eyeLaser['currentAngle']
            if self.distanceToBeam(player.rect.center, start, angle) <= threshold:
                return True
        return False

    def distanceToBeam(self, point, start, angle):
        px, py = point
        sx, sy = start
        dx, dy = math.cos(angle), math.sin(angle)
        return abs((px - sx) * dy - (py - sy) * dx)

    def endState(self):
        self.state = None
        self.data.clear()
        self.lasers.clear()
        self.warnPoints.clear()

    def draw(self, screen):
        if self.warnPoints:
            surf = pygame.Surface((self.enemy.screenW, self.enemy.screenH), pygame.SRCALPHA)
            warnRadius = int(const.scaleValue(14, self.screen[0], self.screen[1]))
            warnWidth = max(1, int(const.scaleValue(2, self.screen[0], self.screen[1])))
            for x, y in self.warnPoints:
                pygame.draw.circle(surf, (*const.yellow[:3], 140), (int(x), int(y)), warnRadius, warnWidth)
            screen.blit(surf, (0,0))

        if getattr(self, 'eyeLaser', None) is not None:
            surf = pygame.Surface((self.enemy.screenW, self.enemy.screenH), pygame.SRCALPHA)
            start = self.eyeLaser['start']
            angle = self.eyeLaser['currentAngle']
            stage = self.eyeLaser.get('stage')
            if stage == 'tele':
                color = (255, 220, 60, 120)
                width = max(1, int(const.scaleValue(3, self.screen[0], self.screen[1])))
            elif stage == 'hold':
                color = (255, 220, 60, 180)
                width = max(1, int(const.scaleValue(4, self.screen[0], self.screen[1])))
            elif stage == 'fire':
                color = (255, 220, 60, 255)
                width = max(2, int(const.scaleValue(10, self.screen[0], self.screen[1])))
            else:
                color = (255, 220, 60, 0)
                width = 0
            if width > 0:
                end = (start[0] + math.cos(angle) * 3000, start[1] + math.sin(angle) * 3000)
                pygame.draw.line(surf, color, start, end, width)
            screen.blit(surf, (0,0))

        if self.lasers:
            surf = pygame.Surface((self.enemy.screenW, self.enemy.screenH), pygame.SRCALPHA)
            beamWidth = max(1, int(const.scaleValue(4 if not self.desperation else 8, self.screen[0], self.screen[1])))
            color = (255, 200, 40, 140) if not self.desperation else (255,120,40,200)
            for laser in self.lasers:
                start = laser["pos"]
                angle = laser["angle"]
                end = (start[0] + math.cos(angle) * 3000, start[1] + math.sin(angle) * 3000)
                pygame.draw.line(surf, color, start, end, beamWidth)
            screen.blit(surf, (0,0))


    def usePhaseTwoImage(self):
        if self.phaseTwoImage is None:
            self.phaseTwoImage = pygame.image.load(const.enemyPths["bossFiveTwo"]).convert_alpha()
        center                 = self.enemy.rect.center
        self.enemy.image       = pygame.transform.scale(self.phaseTwoImage, self.enemy.image.get_size())
        self.enemy.rect        = self.enemy.image.get_rect(center=center)
        self.enemy.posX        = float(self.enemy.rect.x)
        self.enemy.posY        = float(self.enemy.rect.y)

    def usePhaseThreeImage(self):
        if self.phaseThreeImage is None:
            self.phaseThreeImage = pygame.image.load(const.enemyPths["bossFiveThree"]).convert_alpha()
        center                 = self.enemy.rect.center
        self.enemy.image       = pygame.transform.scale(self.phaseTwoImage, self.enemy.image.get_size())
        self.enemy.rect        = self.enemy.image.get_rect(center=center)
        self.enemy.posX        = float(self.enemy.rect.x)
        self.enemy.posY        = float(self.enemy.rect.y)