import pygame
from mapping.maps import getExitTiles, getWallRects, getElevatorTiles
from entitity.bullet import bullet

class player(pygame.sprite.Sprite):
    immuFrameTime = 0.5
    size          = (60, 60)
    speed         = 220
    shootCooldown = 0.25

    def __init__(self, screenW, screenH):
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
        mouseX, mouseY = pygame.mouse.get_pos()
        newBullet = bullet(self.rect.centerx, self.rect.centery, mouseX, mouseY, owner="player")
        self.bullets.add(newBullet)
        self.shootTimer = self.shootCooldown

    def update(self, deltaTime, currentRoomId):
        if self.invincibilityTimer > 0:
            self.invincibilityTimer -= deltaTime

        if self.shootTimer > 0:
            self.shootTimer -= deltaTime

        #shoots bullet on left click
        if pygame.mouse.get_pressed()[0] and self.shootTimer <= 0:
            self.shoot()

        keyState = pygame.key.get_pressed()
        dx, dy = 0, 0
        if keyState[pygame.K_a] or keyState[pygame.K_LEFT]:  dx -= 1
        if keyState[pygame.K_d] or keyState[pygame.K_RIGHT]: dx += 1
        if keyState[pygame.K_w] or keyState[pygame.K_UP]:    dy -= 1
        if keyState[pygame.K_s] or keyState[pygame.K_DOWN]:  dy += 1

        moveVec = pygame.Vector2(dx, dy)
        if moveVec.length() > 0:
            moveVec = moveVec.normalize() * self.speed * deltaTime

        self.moveAndCollide(moveVec, currentRoomId)

        self.bullets.update(deltaTime, self.screenW, self.screenH)

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