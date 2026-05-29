import pygame
import const

from entity.weapons.bullet import bullet
from entity.weapons.weaponReader import weapon

from mapping.mapLogic.chestLogic import chest
from mapping.maps import getExitTiles, getWallRects, getElevatorTiles, getBreakableRectsWithCoords, breakTile, getChestRectsWithCoords


class player(pygame.sprite.Sprite):
    immuFrameTime  = 0.5
    dodgeKey       = pygame.K_f

    #these are tiles per second
    gridPS          = 0.25
    dodgeGridPS     = 2


    dodgeCooldown  = 0.5
    roomCols       = 15
    roomRows       = 9

    def __init__(self, screenW, screenH, size = (60,60), gun=None ):
        super().__init__()
        self.size               = size
        self.screenW            = screenW
        self.screenH            = screenH
        self.hp                 = 6
        self.maxHp              = 6
        self.image              = None
        self.rect               = pygame.Rect(0, 0, self.size[0], self.size[1])
        self.respawn(screenW, screenH)
        self.invincibilityTimer = 0.0
        self.isAlive            = True
        self.shootTimer         = 0.0
        self.bullets            = pygame.sprite.Group()
        self.posX               = float(self.rect.x)
        self.posY               = float(self.rect.y)
        self.chestRegistry      = {}
        self.dodging            = False
        self.dodgeVec           = pygame.Vector2(0, 0)
        self.dodgeRemaining     = 0.0
        self.dodgeCooldownTimer = 0.0
        self.obtainedGuns       = []
        self.doorsLocked        = False
        self.updateSpeed()

        self.allowShoot = False if gun is None else True

    def getWeapon(self, obtained):
        self.obtainedGuns.append(obtained)
        self.allowShoot    = True
        self.gun           = weapon(obtained)
        self.gun.readWeaponSheet()
        self.shootCooldown = float(self.gun.cooldown)

    def respawn(self, screenW, screenH):
        self.screenW     = screenW
        self.screenH     = screenH
        self.rect.center = (screenW // 2, screenH // 2)
        self.posX        = float(self.rect.x)
        self.posY        = float(self.rect.y)

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
            newBullet = bullet(self.rect.centerx, self.rect.centery, mouseX, mouseY,(self.screenW,self.screenH), owner="player")
            self.bullets.add(newBullet)
            self.shootTimer = self.shootCooldown

    def playerToucherHelper(self, otherRect):
        sides1 = [self.rect.right, self.rect.left, self.rect.bottom, self.rect.top]
        sides2 = [otherRect.left, otherRect.right, otherRect.top, otherRect.bottom]
        return any(s1 == s2 for s1, s2 in zip(sides1, sides2))

    def syncPos(self):
        self.posX = float(self.rect.x)
        self.posY = float(self.rect.y)

    def startDodge(self, dx, dy):
        if self.dodging or self.dodgeCooldownTimer > 0:
            return

        if dx != 0 or dy != 0:
            direction = pygame.Vector2(dx, dy).normalize()
        else:
            mx, my    = pygame.mouse.get_pos()
            toMouse   = pygame.Vector2(mx - self.rect.centerx, my - self.rect.centery)
            direction = toMouse.normalize() if toMouse.length() > 0 else pygame.Vector2(1, 0)




        tileW             = self.screenW / self.roomCols
        tileH             = self.screenH / self.roomRows



        dodgeDist         = 1.5 * min(tileW, tileH) #distance of dodge

        self.dodging          = True
        self.dodgeVec         = direction
        self.dodgeRemaining   = dodgeDist
        self.invincibilityTimer = max(self.invincibilityTimer,
                                      dodgeDist / self.dodgeSpeed + 0.05)

    def update(self, deltaTime, currentRoomId, currentLayerID, currentRoomPosX=0, currentRoomPosY=0, keybinds=None):
        if self.invincibilityTimer > 0:
            self.invincibilityTimer -= deltaTime

        if self.shootTimer > 0:
            self.shootTimer -= deltaTime

        if self.dodgeCooldownTimer > 0:
            self.dodgeCooldownTimer -= deltaTime

        shootBtn = keybinds["shoot"] if keybinds else 1
        if shootBtn <= 3:
            if pygame.mouse.get_pressed()[shootBtn - 1] and self.shootTimer <= 0:
                self.shoot()



            #TEMP CODE
                #self.doorsLocked = False
            #====================






        keyState = pygame.key.get_pressed()

        if keybinds:
            upKey    = keybinds["up"]
            downKey  = keybinds["down"]
            leftKey  = keybinds["left"]
            rightKey = keybinds["right"]
            interact = keybinds["interact"]
            dodgeKey = keybinds["dodge"]
        else:
            upKey, downKey, leftKey, rightKey, interact, dodgeKey = (
                pygame.K_w, pygame.K_s, pygame.K_a, pygame.K_d, pygame.K_RETURN, pygame.K_f
            )

        dx, dy = 0, 0
        if keyState[leftKey]  or keyState[pygame.K_LEFT]:  dx -= 1
        if keyState[rightKey] or keyState[pygame.K_RIGHT]: dx += 1
        if keyState[upKey]    or keyState[pygame.K_UP]:    dy -= 1
        if keyState[downKey]  or keyState[pygame.K_DOWN]:  dy += 1

        if keyState[dodgeKey] and not self.dodging and self.dodgeCooldownTimer <= 0:
            self.startDodge(dx, dy)





        #chest lpogic=================================================
        chestRectStuff = getChestRectsWithCoords(currentRoomId, self.screenW, self.screenH)

        for chestData in chestRectStuff:
            chestKey = (int(currentRoomPosX), int(currentRoomPosY),
                        int(chestData["col"][0]), int(chestData["col"][1]))

            if chestKey not in self.chestRegistry:
                self.chestRegistry[chestKey] = chest(currentLayerID)
                print(f"player: registered chest at {chestKey}")

            if self.playerToucherHelper(chestData["rect"]) and keyState[interact]:
                chestObj = self.chestRegistry[chestKey]
                loot = chestObj.openChest()
                if loot is not None:
                    self.getWeapon(loot)
                    print(f"player: got {loot} from chest {chestKey}")





        #dodge logic============================================================
        if self.dodging:
            #move at dodge speed
            maxStep      = self.dodgeSpeed * deltaTime
            step         = min(maxStep, self.dodgeRemaining)
            dodgeMoveVec = self.dodgeVec * step

            prevX, prevY = self.posX, self.posY
            self.moveAndCollide(dodgeMoveVec, currentRoomId)

            #ensure it stops at wall
            actualDist = pygame.Vector2(self.posX - prevX, self.posY - prevY).length()
            self.dodgeRemaining -= actualDist

            #end
            if self.dodgeRemaining <= 0 or actualDist < step * 0.5:
                self.dodging            = False
                self.dodgeRemaining     = 0.0
                self.dodgeCooldownTimer = self.dodgeCooldown
        else:
            moveVec = pygame.Vector2(dx, dy)
            if moveVec.length() > 0:
                moveVec = moveVec.normalize() * self.speed * deltaTime
            self.moveAndCollide(moveVec, currentRoomId)





        #bullet deals================================================================
        wallRects     = getWallRects(currentRoomId, self.screenW, self.screenH)
        breakableData = getBreakableRectsWithCoords(currentRoomId, self.screenW, self.screenH)

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

        self.posX   += moveVec.x
        self.rect.x  = int(self.posX)
        for wallRect in wallRects:
            if self.rect.colliderect(wallRect):
                if moveVec.x > 0:
                    self.rect.right = wallRect.left
                else:
                    self.rect.left  = wallRect.right
                self.posX = float(self.rect.x)

        self.posY   += moveVec.y
        self.rect.y  = int(self.posY)
        for wallRect in wallRects:
            if self.rect.colliderect(wallRect):
                if moveVec.y > 0:
                    self.rect.bottom = wallRect.top
                else:
                    self.rect.top    = wallRect.bottom
                self.posY = float(self.rect.y)

        self.rect.clamp_ip(pygame.Rect(0, 0, self.screenW, self.screenH))

        clampedX = float(self.rect.x)
        clampedY = float(self.rect.y)
        if clampedX != int(self.posX):
            self.posX = clampedX
        if clampedY != int(self.posY):
            self.posY = clampedY

    def touchingExit(self, roomId):
        if not self.doorsLocked:
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

    def rescaleSprite(self):
        self.image = pygame.transform.scale(self.image,(int(self.size[0]), int(self.size[1])))
        center = self.rect.center
        self.rect = self.image.get_rect(center=center)


    def updateSpeed(self):
        self.speed      = self.screenW * self.gridPS
        self.dodgeSpeed = self.screenW * self.dodgeGridPS