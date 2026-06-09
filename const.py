import pygame
import os
import random

black      = (0,0,0)
white      = (255,255,255)
brown      = pygame.Color("#7A5901")
red        = (255,0,0)
cyan       = (0,255,255)
yellow     = (255,255,0)
purple     = (255,0,255)
orange     = pygame.Color("#FFA500")
bulletRed  = pygame.Color("#EE4B2B")
blockSize  = 20
darkgray   = (60,60,60)
green      = (0,255,0)
blue       = (0,0,255)

roomCols   = 9
roomRows   = 15


baseDir    = os.path.dirname(os.path.abspath(__file__))
playerDir  = os.path.join(baseDir, "assets", "pictures", "entities", "player.png")
bulletDir  = os.path.join(baseDir, "assets", "pictures", "entities", "bullet.png")

mapDirs    = os.path.join(baseDir, "assets","maps")
chest      = os.path.join(mapDirs, "chest.png")
elevator   = os.path.join(mapDirs, "elevator.png")
wall       = os.path.join(mapDirs, "wall.png")
doorO      = os.path.join(mapDirs, "doorOpen.png")
doorL      = os.path.join(mapDirs, "doorLocked.png")
box        = os.path.join(mapDirs, "box.png")
shopImg    = os.path.join(mapDirs, "shop.png")

caineDir  = os.path.join(baseDir, "assets","caine")



enemyDirs = os.path.join(baseDir,"assets","pictures","enemies")


enemyPths = {
    "fodder": os.path.join(enemyDirs, "fodder.png"),
    "triplet": os.path.join(enemyDirs, "triplet.png"),
    "bossOne": os.path.join(enemyDirs, "bossOne.png"),
    "machineGunner": os.path.join(enemyDirs, "machineGunner.png"),
    "shotgunner": os.path.join(enemyDirs, "shotgunner.png"),
    "sniper": os.path.join(enemyDirs, "sniper.png"),
    "bossTwo": os.path.join(enemyDirs, "bossTwo.png"),
    "bossThree": os.path.join(enemyDirs, "bossThree.png"),
    "bouncyShotgunner" : os.path.join(enemyDirs, "bouncyShotgunner.png"),
    "bossFour": os.path.join(enemyDirs, "farag.png"),
    "bossFourPhaseTwo": os.path.join(enemyDirs, "pharoh.png"),
}


UIElements = os.path.join(baseDir, "assets","pictures","UIelements")
fullHeart  = os.path.join(UIElements, "heart","fullheart.png")
halfHeart  = os.path.join(UIElements, "heart","halfheart.png")
loseSceren = os.path.join(UIElements,"lose.png")
money      = os.path.join(UIElements,"money.png")
shopKeeper = os.path.join(UIElements, "shopKeeper.png")
healingPot = os.path.join(UIElements, "healingPotion.png")


# keyano is a poo poo head



def enemySpawnCount(layerID, difficultyMultiplier):
    enemySpawnAmount = {
        0: {
            1: 0,
            2: 0,
            3: 0,
            4: 0,
            5: 0,
            6: 0,
            7: 0,
            8: 0,
            9: 0,
        },
        0.25: {
            1: 0,
            2: random.randint(0, 1),
            3: random.randint(0, 1),
            4: random.randint(0, 2),
            5: random.randint(0, 2),
            6: random.randint(0, 3),
            7: random.randint(0, 3),
            8: random.randint(1, 3),
            9: random.randint(1, 3),
        },
        0.5: {
            1: random.randint(0, 1),
            2: random.randint(0, 2),
            3: random.randint(1, 2),
            4: random.randint(1, 2),
            5: random.randint(1, 3),
            6: random.randint(1, 3),
            7: random.randint(2, 3),
            8: random.randint(2, 3),
            9: random.randint(3, 4),
        },
        1: {
            1: random.randint(2, 4),
            2: random.randint(3, 4),
            3: random.randint(3, 5),
            4: random.randint(4, 5),
            5: random.randint(4, 6),
            6: random.randint(5, 6),
            7: random.randint(5, 7),
            8: random.randint(6, 7),
            9: random.randint(6, 9),
        },
        1.25: {
            1: random.randint(3, 6),
            2: random.randint(4, 7),
            3: random.randint(5, 8),
            4: random.randint(6, 9),
            5: random.randint(7, 10),
            6: random.randint(8, 11),
            7: random.randint(9, 12),
            8: random.randint(10, 13),
            9: random.randint(11, 14),
        },
        1.5: {
            1: random.randint(5, 8),
            2: random.randint(6, 9),
            3: random.randint(7, 10),
            4: random.randint(8, 11),
            5: random.randint(9, 12),
            6: random.randint(10, 13),
            7: random.randint(11, 14),
            8: random.randint(12, 15),
            9: random.randint(14, 16),
        },
        2: {
            1: random.randint(1, 2),
            2: random.randint(2, 4),
            3: random.randint(3, 8),
            4: random.randint(4, 16),
            5: random.randint(5, 32),
            6: random.randint(6, 64),
            7: random.randint(7, 128),
            8: random.randint(8, 256),
            9: random.randint(9, 512),
        }
    }
    #S(L) = floor((10 - D)D * min(1, L / (12 - 4D)))+ceil(3*D)
    #D ∈ {0, 0.25, 0.5, 1, 1.25, 1.5, 2}
    #S(L)=\operatorname{floor}((10-D)D*\min(1,L/(12-4D)))+\operatorname{ceil}\left(3\cdot D\right)\left\{0<L\ \le9\right\}
    """    return (math.floor((10-difficultyMultiplier) *
                      difficultyMultiplier*min(1,layerID/(12-4 * difficultyMultiplier)))
            + math.ceil(3*difficultyMultiplier))"""
    return enemySpawnAmount[difficultyMultiplier][layerID]



difficultyStats = {
    "redacted": {"multiplier": 0.1,  "bulletSpeed": 0.1,  "dashFrames": 10000.0, "enemyCount": 0.1,  "enemyHp": 1.0},
    "ign"     : {"multiplier": 0.25, "bulletSpeed": 0.25, "dashFrames": 2.0,     "enemyCount": 0.25, "enemyHp": 1.0},
    "easy"    : {"multiplier": 0.5,  "bulletSpeed": 0.5,  "dashFrames": 1.5,     "enemyCount": 0.5,  "enemyHp": 1.0},
    "normal"  : {"multiplier": 1.0,  "bulletSpeed": 1.0,  "dashFrames": 1.25,    "enemyCount": 1.0,  "enemyHp": 1.0},
    "hard"    : {"multiplier": 1.25, "bulletSpeed": 1.05, "dashFrames": 1.0,     "enemyCount": 1.25, "enemyHp": 1.0},
    "farag"   : {"multiplier": 1.5,  "bulletSpeed": 1.08,  "dashFrames": 0.75,    "enemyCount": 1.5,  "enemyHp": 1.25},
    "nagra"   : {"multiplier": 2.0,  "bulletSpeed": 1.1,  "dashFrames": 0.5,     "enemyCount": 2.0,  "enemyHp": 1.5},
}

difficultyOptions = list(difficultyStats.keys())

fontTextBasic = None

enemySpawnIndicatorColor = red #anastasia said so

gunPaths = os.path.join(baseDir, "assets","guns")
gunPths = {
    "basicPistol": os.path.join(gunPaths, "basicPistol.png"),
    "burstPistol": os.path.join(gunPaths, "burstPistol.png"),
    "basicShotgun":os.path.join(gunPaths, "basicShotgun.png"),
    "assaultRifle":os.path.join(gunPaths, "assaultRifle.png"),
    "bounceBurst" : os.path.join(gunPaths, "bounceBurst.png"),
    "machineGun"  : os.path.join(gunPaths, "machineGun.png"),
    "bShotgun"    : os.path.join(gunPaths, "shotgun.png")

}
