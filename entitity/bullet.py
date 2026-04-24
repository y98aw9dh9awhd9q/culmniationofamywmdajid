import pygame
import math

class bullet(pygame.sprite.Sprite):
    def __init__(self,pos,facingDir, vel = 2):
        super().__init__()
        self.pos       = pygame.math.Vector2(pos)
        self.facingDir = math.radians(facingDir)
        self.vel       = pygame.math.Vector2(1,0).rotate(-facingDir)*vel
        self.image     = None
        self.size      = (60,60)
        self.rect = pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])


    def update(self):

        self.pos += self.vel
        print(self.vel)