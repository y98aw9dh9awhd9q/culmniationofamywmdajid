import pygame
from mapping.maps import getExitTiles, getWallRects, getElevatorTiles, getBreakableRectsWithCoords, breakTile
from entity.weapons.bullet import bullet
from entity.weapons.weaponReader import weapon

class player(pygame.sprite.Sprite):
    immuFrameTime = 0.5
    size          = (60, 60)
    speed         = 220

    def __init__(self, screenW, screenH, gun = None):
        super().__init__()
        self.screenW = screenW
        self.screenH = screenH
        self.hp      = 6
        self.maxHp   = 6
        self.image   = None
        self.rect    = pygame.Rect(0, 0, self.size[0], self.size[1])
        self.respawn(screenW, screenH)
        self.invincibilityTimer = 0.0
        self.isAlive            = True
        self.shootTimer         = 0.0
        self.bullets            = pygame.sprite.Group()

        if gun is None:
            self.allowShoot = False

    def getWeapon(self, obtained):
        self.allowShoot = True
        self.gun = weapon(obtained)
        self.gun.readWeaponSheet()
        self.shootCooldown = float(self.gun.cooldown)


    def respawn(self, screenW, screenH):
        self.screenW     = screenW
        self.screenH     = screenH
        self.rect.center = (screenW // 2, screenH // 2)

    def takeDamage(self):
        if self.invincibilityTimer > 0:
            return
        self.hp                -= 1
        self.invincibilityTimer = self.immuFrameTime
        if self.hp <= 0:
            self.isAlive = False

    def isFlickering(self):
        return self.invincibilityTimer > 0 and int(self.invincibilityTimer * 10) % 2 == 0

    def shoot(self):
        if self.allowShoot:
            mouseX, mouseY = pygame.mouse.get_pos()
            newBullet = bullet(self.rect.centerx, self.rect.centery, mouseX, mouseY, owner="player")
            self.bullets.add(newBullet)
            self.shootTimer = self.shootCooldown

    def update(self, deltaTime, currentRoomId, keybinds=None):
        if self.invincibilityTimer > 0:
            self.invincibilityTimer -= deltaTime

        if self.shootTimer > 0:
            self.shootTimer -= deltaTime

        shootBtn = keybinds["shoot"] if keybinds else 1
        if shootBtn <= 3:
            if pygame.mouse.get_pressed()[shootBtn - 1] and self.shootTimer <= 0:
                self.shoot()
        elif pygame.key.get_pressed()[shootBtn] and self.shootTimer <= 0:
            self.shoot()



        keyState = pygame.key.get_pressed()

        if keybinds:
            upKey    = keybinds["up"]
            downKey  = keybinds["down"]
            leftKey  = keybinds["left"]
            rightKey = keybinds["right"]
        else:
            upKey, downKey, leftKey, rightKey = pygame.K_w, pygame.K_s, pygame.K_a, pygame.K_d

        dx, dy = 0, 0
        if keyState[leftKey]  or keyState[pygame.K_LEFT]:  dx -= 1
        if keyState[rightKey] or keyState[pygame.K_RIGHT]: dx += 1
        if keyState[upKey]    or keyState[pygame.K_UP]:    dy -= 1
        if keyState[downKey]  or keyState[pygame.K_DOWN]:  dy += 1

        moveVec = pygame.Vector2(dx, dy)
        if moveVec.length() > 0:
            moveVec = moveVec.normalize() * self.speed * deltaTime

        self.moveAndCollide(moveVec, currentRoomId)

        wallRects      = getWallRects(currentRoomId, self.screenW, self.screenH)
        breakableData  = getBreakableRectsWithCoords(currentRoomId, self.screenW, self.screenH)

        def onBreak(rowIdx, colIdx):
            breakTile(currentRoomId, rowIdx, colIdx)

        for b in list(self.bullets):
            b.update(deltaTime, self.screenW, self.screenH,
                     wallRects=wallRects, breakableData=breakableData, onBreak=onBreak)

        if self.touchingExit(currentRoomId):
            return self.touchingExit(currentRoomId)
        elif self.touchingElevator(currentRoomId):
            return self.touchingElevator(currentRoomId)

    def moveAndCollide(self, moveVec, roomId):
        wallRects = getWallRects(roomId, self.screenW, self.screenH)

        self.rect.x += moveVec.x
        for wallRect in wallRects:
            if self.rect.colliderect(wallRect):
                if moveVec.x > 0: self.rect.right = wallRect.left
                else:             self.rect.left  = wallRect.right

        self.rect.y += moveVec.y
        for wallRect in wallRects:
            if self.rect.colliderect(wallRect):
                if moveVec.y > 0: self.rect.bottom = wallRect.top
                else:             self.rect.top    = wallRect.bottom

        self.rect.clamp_ip(pygame.Rect(0, 0, self.screenW, self.screenH))

    def touchingExit(self, roomId):
        for exitRect in getExitTiles(roomId, self.screenW, self.screenH):
            rect, direction = exitRect
            if self.rect.colliderect(rect):
                return direction
        return None

    def touchingElevator(self, roomID):
        if roomID == -1:
            return None
        elif roomID == -2 and self.rect.colliderect(getElevatorTiles(roomID, self.screenW, self.screenH)):
            return True