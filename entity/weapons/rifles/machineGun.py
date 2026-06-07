from entity.weapons.gunClass import gun
from entity.weapons.bullet import bullet
import pygame

class machineGunClass(gun):
    def __init__(self):
        super().__init__(0.04, "machineGun")

        self.burstShotsRemaining = 0
        self.burstDelay          = 0.05
        self.burstTimer          = 0
        self.targetX             = 0
        self.targetY             = 0
        self.reloadCooldown      = 15.0
        self.reloadTimer         = 0.0

    def shoot(self, player):
        if self.reloadTimer > 0 or self.burstShotsRemaining > 0:
            return

        self.burstShotsRemaining = 50
        self.burstTimer          = 0

    def fireBullet(self, player):
        player.bullets.add(
            bullet(
                player.rect.centerx,
                player.rect.centery,
                self.targetX,
                self.targetY,
                (player.screenW, player.screenH),
                owner      = "player",
                difficulty = player.difficulty
            )
        )
        self.burstShotsRemaining -= 1

    def update(self, player, deltaTime):
        mx, my                   = pygame.mouse.get_pos()
        self.targetX             = mx
        self.targetY             = my

        if self.reloadTimer > 0:
            self.reloadTimer -= deltaTime
            return

        if self.burstShotsRemaining <= 0:
            return

        self.burstTimer -= deltaTime
        if self.burstTimer <= 0:
            self.fireBullet(player)
            self.burstTimer = self.burstDelay

            if self.burstShotsRemaining == 0:
                self.reloadTimer = self.reloadCooldown