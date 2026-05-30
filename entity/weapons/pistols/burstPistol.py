from entity.weapons.gunClass import gun
from entity.weapons.bullet import bullet
import pygame

class burstPistolClass(gun):
    def __init__(self):
        super().__init__(0.6, "burstPistol")

        self.burstShotsRemaining = 0
        self.burstDelay          = 0.12
        self.burstTimer          = 0
        self.targetX             = 0
        self.targetY             = 0

    def shoot(self, player):
        mx, my                   = pygame.mouse.get_pos()
        self.targetX             = mx
        self.targetY             = my
        self.burstShotsRemaining = 3
        self.burstTimer          = 0

        self.fireBullet(player)

    def fireBullet(self, player):
        player.bullets.add(
            bullet(
                player.rect.centerx,
                player.rect.centery,
                self.targetX,
                self.targetY,
                (player.screenW, player.screenH),
                owner="player",
                difficulty=player.difficulty
            )
        )

        self.burstShotsRemaining -= 1

    def update(self, player, deltaTime):
        if self.burstShotsRemaining <= 0:
            return

        self.burstTimer -= deltaTime

        if self.burstTimer <= 0:
            self.fireBullet(player)
            self.burstTimer = self.burstDelay