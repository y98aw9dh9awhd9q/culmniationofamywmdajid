import pygame
import random
from entity.weapons.bullet import bullet
from mapping.maps import getWallRects, getBreakableRectsWithCoords,breakTile

#extremely basic ai, shotos then moves to a valid cell



class fodderAIClass:
    shootCooldown  = 2.0
    moveSpeed      = 80
    moveInterval   = 1.5

    def __init__(self, enemy, screen, difficulty):
        self.enemy         = enemy
        self.shootTimer    = random.uniform(0, self.shootCooldown)
        self.moveTimer     = 0.0
        self.targetX       = float(enemy.posX)
        self.targetY       = float(enemy.posY)
        self.bullets       = pygame.sprite.Group()
        self.screen        = screen
        self.difficulty    = difficulty

    def update(self, deltaTime, roomId, player):
        self.shootTimer -= deltaTime
        self.moveTimer  -= deltaTime

        self.handleShooting(player)
        self.handleMovement(deltaTime, roomId)
        wallRects = getWallRects(roomId, self.enemy.screenW, self.enemy.screenH)

        breakableData = getBreakableRectsWithCoords(roomId, self.enemy.screenW, self.enemy.screenH)

        def onBreak(rowIdx, colIdx):
            breakTile(roomId, rowIdx, colIdx)

        self.bullets.update(
            deltaTime,
            self.enemy.screenW,
            self.enemy.screenH,
            wallRects=wallRects,
            breakableData=breakableData,
            onBreak=onBreak
        )

    def draw(self, screen):
        self.bullets.draw(screen)

    def handleShooting(self, player):
        if self.shootTimer > 0:
            return
        self.shootTimer = self.shootCooldown

        cx, cy   = self.enemy.rect.centerx, self.enemy.rect.centery
        px, py   = player.rect.centerx,     player.rect.centery

        newBullet = bullet(
            cx, cy, px, py,
            size   = (8, 8),
            color  = (220, 60, 60),
            damage = self.enemy.atk,
            owner  = "enemy",
            screen = self.screen,
            difficulty = self.difficulty
        )
        self.bullets.add(newBullet)


    #movement handler
    def handleMovement(self, deltaTime, roomId):
        if self.moveTimer <= 0:
            self.moveTimer = self.moveInterval
            self.pickTargetCell(roomId)

        #step towards the target
        dx = self.targetX - self.enemy.posX
        dy = self.targetY - self.enemy.posY
        dist = (dx**2 + dy**2) ** 0.5

        if dist > 2:
            moveVec = pygame.Vector2(dx, dy).normalize() * self.moveSpeed * deltaTime
            self.enemy.moveAndCollide(moveVec, roomId)
        #if arr wait for the next move tick

    def pickTargetCell(self, roomId):
        """#takes a random air tile and then moves the player hthere"""
        from mapping.maps import roomRegistery
        layout   = roomRegistery[roomId].layout
        rowCount = len(layout)
        colCount = len(layout[0])
        blockW   = self.enemy.screenW / colCount
        blockH   = self.enemy.screenH / rowCount

        freeCells = [(row, col) for row, rowData in enumerate(layout) for col, tile   in enumerate(rowData) if tile == 0]

        if not freeCells:
            return

        row, col     = random.choice(freeCells)
        self.targetX = col * blockW + blockW / 2 - self.enemy.rect.width  / 2
        self.targetY = row * blockH + blockH / 2 - self.enemy.rect.height / 2