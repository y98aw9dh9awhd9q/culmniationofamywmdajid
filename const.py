import pygame
import os

black     = (0,0,0)
white     = (255,255,255)
brown     = pygame.Color("#7A5901")
red       = (255,0,0)
orange    = pygame.Color("#FFA500")
bulletRed = pygame.Color("#EE4B2B")
blockSize = 20


baseDir   = os.path.dirname(os.path.abspath(__file__))
playerDir = os.path.join(baseDir, "assets","pictures", "player.png")