from entity.weapons.gunClass import gun
from entity.weapons.bullet import bullet
import pygame

class bShotgunClass(gun):
    def __init__(self):
        super().__init__(0.7,"shotgun")

    def shoot(self, player):
        mx, my                 = pygame.mouse.get_pos()
        start                  = pygame.Vector2(player.rect.center)
        direction              = pygame.Vector2(mx-start.x,my-start.y)
        if direction.length() == 0:return
        direction              = direction.normalize()
        angles                 = [-20, -10, 0, 10, 20]

        for angle in angles:
            pelletDir = direction.rotate(angle)
            target    = start + pelletDir * 1000

            player.bullets.add(
                bullet(
                    start.x,
                    start.y,
                    target.x,
                    target.y,
                    (player.screenW, player.screenH),
                    owner="player",
                    difficulty=player.difficulty
                )
            )