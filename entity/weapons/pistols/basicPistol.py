from entity.weapons.gunClass import gun
from entity.weapons.bullet import bullet
import pygame

class basicPistolClass(gun):
    def __init__(self):
        super().__init__(0.25, "basicPistol")

    def shoot(self, player):
        mx, my = pygame.mouse.get_pos()

        player.bullets.add(
            bullet(
                player.rect.centerx,
                player.rect.centery,
                mx, my,
                (player.screenW, player.screenH),
                owner="player",
                difficulty=player.difficulty
            )
        )
