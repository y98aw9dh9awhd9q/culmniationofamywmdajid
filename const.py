import pygame
import os
import math

black     = (0,0,0)
white     = (255,255,255)
brown     = pygame.Color("#7A5901")
red       = (255,0,0)
cyan      = (0,255,255)
yellow    = (255,255,0)
purple    = (255,0,255)
orange    = pygame.Color("#FFA500")
bulletRed = pygame.Color("#EE4B2B")
blockSize = 20

roomCols  = 9
roomRows  = 15


baseDir   = os.path.dirname(os.path.abspath(__file__))
playerDir = os.path.join(baseDir, "assets", "pictures", "entities", "player.png")
bulletDir = os.path.join(baseDir, "assets", "pictures", "entities", "bullet.png")

mapDirs  = os.path.join(baseDir, "assets","maps")
chest    = os.path.join(mapDirs, "chest.png")
elevator = os.path.join(mapDirs, "elevator.png")

caineDir  = os.path.join(baseDir, "assets","caine")



enemyDirs = os.path.join(baseDir,"assets","pictures","enemies")


enemyPths = {
    "fodder": os.path.join(enemyDirs, "fodder.png")

}






# keyano is a poo poo head

def enemySpawnCount(layerID, difficultyMultiplier):
    #S(L) = floor((10 - D)D * min(1, L / (12 - 4D)))+ceil(3*D)
    #D ∈ {0, 0.25, 0.5, 1, 1.25, 1.5, 2}
    #S(L)=\operatorname{floor}((10-D)D*\min(1,L/(12-4D)))+\operatorname{ceil}\left(3\cdot D\right)\left\{0<L\ \le9\right\}
    return (math.floor((10-difficultyMultiplier) *
                      difficultyMultiplier*min(1,layerID/(12-4 * difficultyMultiplier)))
            + math.ceil(3*difficultyMultiplier))


difficultyStats = {
    "redacted": {"multiplier": 0.1,  "bulletSpeed": 0.1,  "dashFrames": 10000.0, "enemyCount": 0.0,  "enemyHp": 1.0},
    "ign"     : {"multiplier": 0.25, "bulletSpeed": 0.25, "dashFrames": 2.0,     "enemyCount": 0.25, "enemyHp": 1.0},
    "easy"    : {"multiplier": 0.5,  "bulletSpeed": 0.5,  "dashFrames": 1.5,     "enemyCount": 0.5,  "enemyHp": 1.0},
    "normal"  : {"multiplier": 1.0,  "bulletSpeed": 1.0,  "dashFrames": 1.25,    "enemyCount": 1.0,  "enemyHp": 1.0},
    "hard"    : {"multiplier": 1.25, "bulletSpeed": 1.25, "dashFrames": 1.0,     "enemyCount": 1.25, "enemyHp": 1.0},
    "farag"   : {"multiplier": 1.5,  "bulletSpeed": 1.5,  "dashFrames": 0.75,    "enemyCount": 1.5,  "enemyHp": 1.5},
    "nagra"   : {"multiplier": 2.0,  "bulletSpeed": 2.0,  "dashFrames": 0.5,     "enemyCount": 2.0,  "enemyHp": 2.0},
}

difficultyOptions = list(difficultyStats.keys())


def getDifficultyStats(name):
    return difficultyStats.get(name, difficultyStats["normal"])


fontTextBasic = None

enemySpawnIndicatorColor = red #anastasia said so

