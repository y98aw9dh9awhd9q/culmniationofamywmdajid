"""
#ben nethaeyahoo and keyahhno acarkey and emotional support horp
#2026-06-07
The Amazing Digital Dungeon!

This is a game inspired by games such as but not limited to:
Enter The Gungeon,
Soul Knight,
most importantly: touhou, and calamity mod,
etc.

This game features a tutorial and interactive menus. The main gameplay is going through 9 layers
with 4 floors each killing every enemy and boss.
"""

import pygame
import asyncio

import const
from gameHelpers.display import display
import data.gameSaveData.dataSaving as dataSaving

import mapping.tutorial.tutorialGen as tutorial
import mapping.mapLogic.mapGenerator as mapGenerator

from   mapping.maps import getEnemySpawns
from   mapping.maps import resetAllRooms

from   entity.player import player
from   entity.entityClass import enemyBuilder
from   entity.enemyLogic.reader.enemySheetReader import getRandomEnemy

import mainMenu.subMenu.settings as settings
import mainMenu.menu as menu
import mainMenu.subMenu.pauseMenu as pauseMenu
from   mainMenu.subMenu.shop import shopInstance
import mainMenu.subMenu.shop as shop


from   gameHelpers.roomDirHelper   import getMatchingEntrance, mapDelta, roomIDer,placePlayerAtDoor
from   gameHelpers.mapGeneration   import generateEntireWorld
from   gameHelpers.display.hud     import drawHud, drawGameOver, drawWinScreen
from   gameHelpers.display.display import spaceCalculator
from   gameHelpers.musMan          import musManager

from data.playerUnlockData.playerData.playerDataManager import writeCompendiumEntry
import gameHelpers.display.enemySpawnIndicator as spawner

from data.playerUnlockData.playerData.playerDataManager import addEnemyKill

#pre boot initialization =========================
print(" main: ",settings.loadSettings())
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode(settings.loadSettings()["resolution"])
clock  = pygame.time.Clock()
font   = pygame.font.SysFont(None, 28)
settings.applySettings(settings.loadSettings())
display.setAssets(screen)
from gameHelpers.animatedGif import preload
gifPaths = [const.enemyPths["bossFourPhaseTwo"], const.enemyPths["bossFourPhaseThree"]]
for i, path in enumerate(gifPaths):
    for event in pygame.event.get():
        pass
    screen.fill(const.black)
    w, h      = screen.get_size()
    barWidth  = int(w * 0.6)
    barHeight = 34
    bx        = (w - barWidth) // 2
    by        = h - barHeight - 24
    progress  = (i + 1) / len(gifPaths)
    pygame.draw.rect(screen, (50, 50, 50), (bx, by, barWidth, barHeight), border_radius=6)
    fillW = int(barWidth * progress)
    if fillW > 0:
        pygame.draw.rect(screen, (0, 200, 0), (bx, by, fillW, barHeight), border_radius=6)
    title = font.render("Loading assets...", True, const.white)
    perc  = font.render(f"{int(progress * 100)}%", True, const.white)
    screen.blit(title, (bx, by - 46))
    screen.blit(perc,  (bx, by - 82))
    pygame.display.flip()
    preload(path)
#menu=============================================
import gameHelpers.menus

menuRes = gameHelpers.menus.mainMenu(screen,clock,font)

tutorialFlag       = menuRes[1]
difficulty         = menuRes[0]

print(f"main recieved menu result {menuRes}")
cfg                = settings.loadSettings()
screen             = settings.applySettings(cfg)
loadedSettings     = settings.loadSettings()


#core vars ===================================
layout, rowCount, colCount, blockW, blockH = display.spaceCalculator(screen, -1)

spriteH, spriteW       = blockH*0.75, blockW*0.75
spriteSize             = (spriteW,spriteH)
playerObj              = player(*screen.get_size(), size=spriteSize, screen = screen)
mapGen                 = mapGenerator.mapGenerator()
generatedMap           = None
currentRoomPosY        = 0
currentRoomPosX        = 0
transitionCooldown     = 0.0
playerSavePrep         = None
worldCache             = {}
tutorialFinished       = False
worldGenerated         = False
worldGenerating        = False
roomIDCompendium       = [(0, 0)]
gameOver               = False
gameOverTimer          = 0.0
gameWin                = False
gameWinTimer           = 0.0
newRoomID              = 0

print(settings.loadSettings)

musicManager = musManager()

musicManager.registerTrack("combat","assets/music/sanctuary.mp3")

#musicManager.registerTrack("shop","assets/music/shop.mp3") NYI

musicManager.registerTrack("bossBossOne","assets/music/antiHeroSwaft.mp3")
musicManager.registerTrack("bossBossTwo","assets/music/ROTJD.mp3")
musicManager.registerTrack("bossBossThree","assets/music/slimeGob.mp3")
musicManager.registerTrack("bossBossFour","assets/music/farowl.mp3")
musicManager.registerTrack("bossBossFive","assets/music/farowl.mp3")
musicManager.registerTrack("bossBossSix","assets/music/farowl.mp3")

#current floor logic===========================

if tutorialFlag:
    print("main: tutorial started")
    currentLayerID = [0, 1]
else:
    print("main: normal layer")
    currentLayerID = [1, 1]

#sprite groups===========================

playerSpriteGroup = pygame.sprite.Group()
playerSpriteGroup.add(playerObj)
enemyGroup        = pygame.sprite.Group()

#save loader=======================
saveDataRead = dataSaving.readSave()
if "1" not in worldCache or "1" not in worldCache.get("1", {}):
    mapGen.size = 3
    mapGen.setupMap(boss=False)
    asyncio.run(mapGen.prGenerateMap())
    worldCache.setdefault("1", {})["1"] = mapGen.result

#new flags ===================================================================
tutorialFinished = False
worldGenerated   = False
worldGenerating  = False

pygame.mixer.music.set_volume(settings.mapVolumeToPygame(loadedSettings["volume"]))

if saveDataRead:
    print("main: loading save")
    (
        playerSaveData,
        _,
        currentLayerID,
        weapon,
        roomIDCompendium,
        fullSave,
        difficulty,
        money,
        inventory,
        playerHP,
        playerMHP
    ) = saveDataRead

    print(f"main: saveDataRead result is {saveDataRead}")

    worldCache = fullSave["worldData"]["layers"]

    #save has full world
    worldGenerated = True
    tutorialFinished = True

    try:
        if playerSaveData is not None:
            currentRoomPosX = playerSaveData[1]
            currentRoomPosY = playerSaveData[2]
            playerObj.rect.center = playerSaveData[3]
        if len(weapon) != 0:
            for weaponItem in weapon:
                print(weaponItem)

                playerObj.getWeapon(weaponItem.replace("Class", ""))

            playerObj.money     = money
            playerObj.inventory = inventory
            playerObj.maxHp     = playerMHP
            playerObj.hp        = playerHP

    except Exception as e:

        print("main: save load error:", e)

else:
    #tutorial mode=========================
    playerObj.money = 10

    if currentLayerID[0] == 0:
        generatedMap = tutorial.tutorialMatching[currentLayerID[1]]
        tutorialFinished = False

    #normal game==================================
    else:
        playerObj.allowShoot = True
        playerObj.getWeapon("basicPistol")
        mapGen.size = 3
        mapGen.setupMap(boss=False)
        asyncio.run(mapGen.prGenerateMap())


        worldCache = {
            "1": {
                "1": mapGen.result
            }
        }

        try:
            generatedMap = worldCache["1"]["1"]
        except KeyError:
            print("main: world missing 1-1?????????")

            mapGen.size = 3
            mapGen.setupMap(boss=False)
            asyncio.run(mapGen.prGenerateMap())

            worldCache.setdefault("1", {})["1"] = mapGen.result
            generatedMap    = worldCache["1"]["1"]

        tutorialFinished    = True
        worldGenerated      = False



        if not tutorialFlag:
            worldGenerating = True
            asyncio.run(generateEntireWorld(mapGen, screen, font, worldCache, difficulty))
            worldGenerated  = True
            worldGenerating = False

        dataSaving.saveGameCall(currentLayerID, playerSavePrep, playerObj, worldCache, roomIDCompendium, difficulty)

def deleteCurrentProgress():
    global worldCache
    global generatedMap
    global currentRoomPosX
    global currentRoomPosY
    global roomIDCompendium
    global currentLayerID

    print("main: deleting current progress")


    worldCache       = {}
    currentRoomPosX  = 0
    currentRoomPosY  = 0
    roomIDCompendium = [(0, 0)]
    currentLayerID   = [1, 1]

    try:
        dataSaving.emptySave()
        dataSaving.deleteSave()
        print("main: save deleted")

    except Exception as e:
        print("main: failed to delete save", e)



def resetRun():
    #oh my globals
    global generatedMap
    global currentRoomPosY
    global currentRoomPosX
    global transitionCooldown
    global playerSavePrep
    global worldCache
    global tutorialFinished
    global worldGenerated
    global worldGenerating
    global roomIDCompendium
    global deathCount
    global gameOver
    global gameOverTimer
    global gameWin
    global gameWinTimer
    global currentLayerID
    global difficulty
    global tutorialFlag
    global newRoomID

    print("main: resetting run")

    deleteCurrentProgress()
    dataSaving.deleteSave()
    musicManager.reset()

    enemyGroup.empty()
    resetAllRooms()
    playerObj.emptyWeapons()
    playerObj.chestRegistry = {}

    for bulletSprite in playerObj.bullets:
        bulletSprite.kill()

    spawnIndicators.clear()

    menuRes = gameHelpers.menus.mainMenu(screen,clock,font)

    tutorialFlag          = menuRes[1]
    difficulty            = menuRes[0]
    tutorialFinished      = False
    worldGenerated        = False
    worldGenerating       = False
    transitionCooldown    = 0.0
    playerSavePrep        = None
    gameOver              = False
    gameOverTimer         = 0
    gameWin               = False
    gameWinTimer          = 0
    deathCount            = 0
    roomIDCompendium      = [(0, 0)]
    playerObj.hp          = playerObj.maxHp
    playerObj.rect.center = screen.get_width() // 2,screen.get_height() // 2
    playerObj.syncPos()
    playerObj.doorsLocked = False
    playerObj.difficulty  = difficulty
    worldCache            = {}
    newRoomID             = 0


    if tutorialFlag:
        currentLayerID    = [0, 1]
    else:
        currentLayerID    = [1, 1]


    if currentLayerID[0] == 0:
        generatedMap      = tutorial.tutorialMatching[currentLayerID[1]]

    else:
        playerObj.allowShoot = True

        if not hasattr(playerObj, "weapon"):
             playerObj.getWeapon("basicPistol")

        mapGen.size = 3
        mapGen.setupMap(boss=False)
        asyncio.run(mapGen.prGenerateMap())
        worldCache = {
            "1": {
                "1": mapGen.result
            }
        }

        generatedMap    = worldCache["1"]["1"]
        worldGenerating = True
        asyncio.run(generateEntireWorld(mapGen,screen,font,worldCache,difficulty))
        worldGenerated  = True
        worldGenerating = False

    tutorial.resetTutorial()

    currentRoomPosX = 0
    currentRoomPosY = 0
    dataSaving.deleteSave()
    resetSpawnEffects()

    print("main: run reset complete")

#load first
if currentLayerID[0] == 0:
    generatedMap = tutorial.tutorialMatching[currentLayerID[1]]
else:
    print(worldCache)
    generatedMap = worldCache[str(currentLayerID[0])][str(currentLayerID[1])]




#enemy helper func

spawnIndicators      = []
spawnEffectsStarted  = False

def resetSpawnEffects():
    global spawnIndicators
    global spawnEffectsStarted
    spawnIndicators.clear()
    spawnEffectsStarted = False

def spawnEnemy(roomID, layerID):
    enemyGroup.empty()
    enemySpawns = getEnemySpawns(roomID,layerID[0],
                                 const.difficultyStats[f"{difficulty}"]["enemyCount"])

    layout, rowCount, colCount, blockW, blockH = display.spaceCalculator(screen, roomID)

    for row, col in enemySpawns:

        enemyX = col * blockW
        enemyY = row * blockH

        enemy = enemyBuilder(
            enemyName = getRandomEnemy(layerID[0]),
            spawnPos  = (enemyX, enemyY),
            layer     = layerID[0],
            screenW   = screen.get_width(),
            screenH   = screen.get_height(),
            difficulty=difficulty
        ) #gridH and the other one isnt needed because this works

        enemyGroup.add(enemy)


def spawnEnemies(screen, roomId, layerId, difficulty,
                 enemySpawnOverrideCountPR=None,
                 enemySpawnBoss=None,
                 bossEnemy=None):
    global spawnEffectsStarted
    layout, rowCount, colCount, blockW, blockH = spaceCalculator(screen, roomId)

    if not spawnEffectsStarted:
        print(f"main enemy spawn override count {enemySpawnOverrideCountPR}")

        enemySpawns = getEnemySpawns(roomID=roomId,
                                     layerID=layerId,
                                     difficulty=difficulty,
                                     enemySpawnOverrideCount=enemySpawnOverrideCountPR)
        rowB, colB = 4,7
        if enemySpawnBoss is None:
            for row, col in enemySpawns:
                spawnIndicators.append(
                    spawner.enemySpawnIndicator(
                        row, col, blockW, blockH,
                        layerID = currentLayerID[0],
                        screenW = screen.get_width(),
                        screenH = screen.get_height(),
                        screen  = screen,
                        difficulty = difficulty,

                    )
                )
        else:
            spawnIndicators.append(
                spawner.enemySpawnIndicator(
                    rowB, colB, blockW, blockH,
                    layerID=6767,
                    screenW=screen.get_width(),
                    screenH=screen.get_height(),
                    screen=screen,
                    difficulty=difficulty,
                    forcedEnemy=bossEnemy,
                )
            )
        spawnEffectsStarted = True

    for indicator in spawnIndicators:
        indicator.update()
        indicator.draw(screen)
        if indicator.spawned and indicator.enemy is not None:
            if indicator.enemy not in enemyGroup:
                enemyGroup.add(indicator.enemy)
                print("main:enemy spawned!")

    spawnIndicators[:] = [indicator for indicator in spawnIndicators if not indicator.done]


def drawBossBar(screen, enemies, font):
    boss = next((enemy for enemy in enemies if enemy.enemyName.lower().startswith("boss")), None)
    if boss is None:
        return

    ai   = boss.ai
    winW = screen.get_width()
    barW = int(winW * 0.58)
    barH = 18
    x    = (winW - barW) // 2
    y    = 18

    label         = getattr(ai,"phaseName")
    if ai is not None and getattr(ai, "desperation", False):
        maxTime   = getattr(ai, "desperationDuration", 30.0)
        remaining = max(0.0, getattr(ai, "desperationTimer", 0.0))
        fillRatio = remaining / maxTime if maxTime > 0 else 0
        label     = f"{getattr(ai,"phaseName")} desperation {remaining:.67f}s"
        fillColor = (255, 80, 40)
    else:
        maxHp     = getattr(ai, "maxHp", boss.hp) if ai is not None else boss.hp
        fillRatio = boss.hp / maxHp if maxHp > 0 else 0
        fillColor = (210, 35, 55)

    fillRatio     = max(0.0, min(1.0, fillRatio))
    pygame.draw.rect(screen, (25, 20, 20), (x, y, barW, barH))
    pygame.draw.rect(screen, fillColor, (x, y, int(barW * fillRatio), barH))
    pygame.draw.rect(screen, const.white, (x, y, barW, barH), 2)

    text          = font.render(label, True, const.white)
    textRect      = text.get_rect(center=(winW // 2, y + barH + 13))
    screen.blit(text, textRect)


#main loop====================================

running = True

while running:

    if len(enemyGroup) ==  0:
        #print("main: doors unlocked")
        playerObj.doorsLocked = False
    elif len(enemyGroup) > 0:
        playerObj.doorsLocked = True


    cfg               = settings.loadSettings()
    deltaTime         = clock.tick(cfg["fpsCap"]) / 1000.0
    events            = pygame.event.get()
    winW, winH        = screen.get_size()
    playerObj.screenW = winW
    playerObj.screenH = winH
    keybinds          = cfg.get("keybinds",settings.defaultSettings["keybinds"])

    if gameOver:
        print("main: game over logic run")
        screen.fill((0, 0, 0))
        drawGameOver(screen)
        gameOverTimer -= deltaTime
        pygame.display.flip()

        #individualized event handler because the other stuff wont run
        for event in events:

            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN and event.key == loadedSettings["keybinds"]["interact"]:
                gameOverTimer = 0

        if gameOverTimer <= 0:
            resetRun()

        continue

    if gameWin:
        screen.fill((0, 0, 0))
        drawWinScreen(screen)
        gameWinTimer -= deltaTime
        pygame.display.flip()

        for event in events:
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == loadedSettings["keybinds"]["interact"]:
                gameWinTimer = 0

        if gameWinTimer <= 0:
            resetRun()

        continue
    #event handler====================================
    for event in events:
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            pauseResult = pauseMenu.run(screen,clock)
            if pauseResult == "save":
                print("main: save game called")
                dataSaving.saveGameCall(currentLayerID, playerSavePrep, playerObj, worldCache, roomIDCompendium, difficulty)
            elif pauseResult == "menu":
                menuResult, screen = menu.run(screen,clock,font)

                if type(menuResult) == tuple:
                    resetRun()

                match menuResult:
                    case "quit": running = False
                    case "infiniteHp":
                        playerObj.hp = 6767
                        playerObj.maxHp = 6767
                        menuResult = None
                    case "allGuns":
                        for gun in playerObj.gunList:
                            playerObj.getWeapon(gun)
                        menuResult = None

                    case "infiniteHeals":
                        for _ in range(1000):
                            playerObj.getItem("HP1")

                    case "teleportToBoss":
                        currentLayerID[1] = 4
                        generatedMap = worldCache[str(currentLayerID[0])][str(currentLayerID[1])]
                        mapSize = len(generatedMap)
                        currentRoomPosY = mapSize - 1
                        currentRoomPosX = mapSize - 2
                        newRoomID = -3
                        playerObj.doorsLocked = True
                        doorRect = getMatchingEntrance(-3, 3, winW, winH, (winW // 2, winH // 2))
                        if doorRect:
                            placePlayerAtDoor(playerObj, doorRect, 3)
                        playerObj.syncPos()
                        spawnEffectsStarted = False
                        roomIDer(currentRoomPosX, currentRoomPosY, roomIDCompendium)
                        playerSavePrep = (
                            newRoomID, currentRoomPosX, currentRoomPosY, playerObj.rect.center
                        )
                        enemyGroup.empty()
                        for bulletSprite in playerObj.bullets:
                            bulletSprite.kill()
                        dataSaving.saveGameCall(currentLayerID, playerSavePrep, playerObj, worldCache, roomIDCompendium, difficulty)
                        menuResult = None






            elif pauseResult == "settings":
                result, screen = settings.run( screen, clock, font)
                layout, rowCount, colCount, blockW, blockH = display.spaceCalculator(screen, -1)
                playerObj.size = (blockW * 0.75, blockH * 0.75)
                playerObj.rescaleSprite()
                playerObj.screenH = screen.get_height()
                playerObj.screenW = screen.get_width()
                playerObj.updateSpeed()
                display.setAssets(screen)
                pygame.mixer.music.set_volume(settings.mapVolumeToPygame(settings.loadSettings()["volume"]))
                if result == "quit":
                    running = False
            elif pauseResult == "quit":
                running = False


    try:
        currentRoomID = generatedMap[currentRoomPosY][currentRoomPosX]
    except IndexError:
        currentRoomPosX = 0
        currentRoomPosY = 0
        currentRoomID = -1
    except Exception as e:
        print(f"main: error caught in room ID process {e}")
    exitDir = playerObj.touchingExit( currentRoomID)


    #elevator=================================
    if playerObj.touchingElevator(currentRoomID):
        if currentLayerID == [6, 4]:
            dataSaving.deleteSave()
            gameWin      = True
            gameWinTimer = 8
            musicManager.stopAll()
            continue

        resetAllRooms()
        shopInstance.resetStock()
        dataSaving.saveGameCall(currentLayerID, playerSavePrep, playerObj, worldCache, roomIDCompendium, difficulty)


        roomIDCompendium = [(0,0)]
        roomIDer(0, 0, roomIDCompendium, True)
        currentRoomPosX = 0
        currentRoomPosY = 0

        match currentLayerID[0]:
            case 2: writeCompendiumEntry("achievements", "bossOne")
            case 3: writeCompendiumEntry("achievements", "bossTwo")
            case 4: writeCompendiumEntry("achievements", "bossThree")
            case 5: writeCompendiumEntry("achievements", "bossFour")
            case 6: writeCompendiumEntry("achievements", "bossFive")
            case 7: writeCompendiumEntry("achievements", "bossSix")

        #tutorial ELEVATOR LOGIC=========================================================
        if currentLayerID[0] == 0:
            if currentLayerID[1] != 4:
                currentLayerID[1] += 1
                generatedMap = tutorial.tutorialMatching[currentLayerID[1]]
            else:
                #tutorial completee!==========================================
                tutorialFinished = True
                currentLayerID[0] = 1
                currentLayerID[1] = 1
                writeCompendiumEntry("achievements", "tutorial")
                currentRoomPosX = 0
                currentRoomPosY = 0


                # generate full world========================
                if not worldGenerated:
                    worldGenerating = True
                    asyncio.run(generateEntireWorld(mapGen, screen, font, worldCache, difficulty))
                    worldGenerated = True
                    worldGenerating = False

                print(worldCache)
                try:
                    generatedMap = worldCache["1"]["1"]
                except KeyError:
                    print("main: world cache missing 1-1")

                    mapGen.size = 3
                    mapGen.setupMap(boss=False)
                    asyncio.run(mapGen.prGenerateMap())
                    worldCache.setdefault("1", {})["1"] = mapGen.result
                    generatedMap = worldCache["1"]["1"]


        #normal floors=========================
        else:
            currentLayerID[1]     += 1
            if currentLayerID[1]   > 4:
                playerObj.increaseMaxHP()
                currentLayerID[0] += 1
                currentLayerID[1]  = 1
                if currentLayerID[0] % 2 != 0: playerObj.increaseHeal()

            if currentLayerID[0]   > 9:
                currentLayerID[0]  = 9
                currentLayerID[1]  = 4

            generatedMap           = worldCache[str(currentLayerID[0])][str(currentLayerID[1])]

        print(f"main: loaded layer: {currentLayerID[0]} - {currentLayerID[1]} ")


    #transition handler
    if exitDir is not None and transitionCooldown <= 0:

        prevCenter          = playerObj.rect.center
        dy, dx              = mapDelta[exitDir]
        newY                = currentRoomPosY + dy
        newX                = currentRoomPosX + dx
        mapH                = len(generatedMap)
        mapW                = len(generatedMap[0])

        if 0 <= newY < mapH and 0 <= newX < mapW:
            currentRoomPosY = newY
            currentRoomPosX = newX
            newRoomID       = generatedMap[currentRoomPosY][currentRoomPosX]
            doorRect        = getMatchingEntrance(
                newRoomID,
                exitDir,
                winW,
                winH,
                prevCenter
            )

            if doorRect:

                placePlayerAtDoor(playerObj,doorRect,exitDir)

                roomIDResult = roomIDer(currentRoomPosX, currentRoomPosY, roomIDCompendium)

                playerObj.syncPos()





            transitionCooldown = 0.25

            playerSavePrep = (
                newRoomID,
                currentRoomPosX,
                currentRoomPosY,
                playerObj.rect.center
            )

            for bulletSprite in playerObj.bullets:
                bulletSprite.kill()

            try:
                print(f"main: new room id {newRoomID}")
                print(f"main:current layeriD: {currentLayerID}spawns: {const.enemySpawnCount(currentLayerID[0],1)}")

                if roomIDResult == "NEW" and (newRoomID >0 or newRoomID == -3) :
                    playerObj.doorsLocked = True
                    spawnEffectsStarted = False
                    print("room locked")



            except Exception as e:
                print("main:no room id", e)

    if transitionCooldown > 0:
        transitionCooldown -= deltaTime


    #render=======================================


    screen.fill((0, 0, 0))  #clears the screen**************

    display.drawRoom(screen, generatedMap[currentRoomPosY][currentRoomPosX], playerObj.doorsLocked)

    playerObj.update(
        deltaTime,
        generatedMap[currentRoomPosY][currentRoomPosX],
        currentLayerID,
        currentRoomPosX,
        currentRoomPosY,
        keybinds
    )

    playerObj.bullets.draw(screen)

    display.drawPlayer(
        screen,
        playerObj
    )

    drawHud(
        screen,
        playerObj,
        generatedMap,
        currentRoomPosY,
        currentRoomPosX,
        roomIDCompendium,
    )

    #bullet handler=====================================================================
    for bullet in list(playerObj.bullets):
        for enemy in list(enemyGroup):

            if enemy.ai and hasattr(enemy.ai, "shieldBlocksBullet"):
                if enemy.ai.shieldBlocksBullet(bullet):
                    bullet.kill()
                    break

            if bullet.rect.colliderect(enemy.rect):
                enemy.takeDamage(bullet.damage)
                bullet.kill()

                if enemy.isDead():
                    addEnemyKill(enemy.enemyName)
                    enemy.kill()
                    playerObj.money += 1+(2*currentLayerID[0])

                break

    #player shot
    for enemy in enemyGroup:
        if enemy.ai is None:
            continue

        if hasattr(enemy.ai, "beamHitsPlayer"):
            if enemy.ai.beamHitsPlayer(playerObj):
                print("main: detected beam hits player")
                playerObj.takeDamage(enemy.atk)
                if playerObj.hp <= 0 and not gameOver:

                    gameOver = True
                    gameOverTimer = 30

                    deleteCurrentProgress()
                    enemyGroup.empty()

                    for bulletSprite in playerObj.bullets:
                        bulletSprite.kill()

                    print("main: player died")

        for bullet in list(enemy.ai.bullets):
            if bullet.rect.colliderect(playerObj.rect):
                print("main: detected player hit")

                playerObj.takeDamage(bullet.damage)
                if playerObj.hp <= 0 and not gameOver:

                    gameOver = True
                    gameOverTimer = 30

                    deleteCurrentProgress()
                    enemyGroup.empty()

                    for bulletSprite in playerObj.bullets:
                        bulletSprite.kill()

                    print("main: player died")

                bullet.kill()

    enemyGroup.update(generatedMap[currentRoomPosY][currentRoomPosX], playerObj, deltaTime)
    for enemy in enemyGroup:
        enemy.draw(screen)
    drawBossBar(screen, enemyGroup, font)

    #tutorial special case enemy spawns
    if currentLayerID[0] == 0:
        tutorial.runTutorial(screen, clock, currentLayerID, currentRoomID,playerObj)
        if currentLayerID[1] == 4 and newRoomID == 33:
            spawnEnemies(screen, currentRoomID, currentLayerID[0], const.difficultyStats[f"{difficulty}"]["enemyCount"],1)
        if currentLayerID[1]==4 and newRoomID == -3:
            spawnEnemies(screen, currentRoomID, currentLayerID[0], const.difficultyStats[f"{difficulty}"]["enemyCount"],3)

    else:
        if newRoomID > 0:
            spawnEnemies(screen,newRoomID,currentLayerID[0],const.difficultyStats[difficulty]["enemyCount"])
        if newRoomID == -3:
            match currentLayerID[0]:
                case 1:
                    spawnEnemies(screen, currentRoomID, currentLayerID[0],
                         const.difficultyStats[f"{difficulty}"]["enemyCount"],
                         1,
                         enemySpawnBoss=True,
                         bossEnemy="bossOne")
                    musicManager.startBoss("BossOne")
                case 2:
                    spawnEnemies(screen, currentRoomID, currentLayerID[0],
                         const.difficultyStats[f"{difficulty}"]["enemyCount"],
                         1,
                         enemySpawnBoss=True,
                         bossEnemy="bossTwo")
                    musicManager.startBoss("BossTwo")

                case 3:
                    spawnEnemies(screen, currentRoomID, currentLayerID[0],
                         const.difficultyStats[f"{difficulty}"]["enemyCount"],
                         1,
                         enemySpawnBoss=True,
                         bossEnemy="bossThree")
                    musicManager.startBoss("BossThree")

                case 4:
                    spawnEnemies(screen, currentRoomID, currentLayerID[0],
                         const.difficultyStats[f"{difficulty}"]["enemyCount"],
                         1,
                         enemySpawnBoss=True,
                         bossEnemy="bossFour")
                    musicManager.startBoss("BossFour")

                case 5:
                    spawnEnemies(screen, currentRoomID, currentLayerID[0],
                         const.difficultyStats[f"{difficulty}"]["enemyCount"],
                         1,
                         enemySpawnBoss=True,
                         bossEnemy="bossFive")
                    musicManager.startBoss("BossFive")

                case 6:
                    spawnEnemies(screen, currentRoomID, currentLayerID[0],
                         const.difficultyStats[f"{difficulty}"]["enemyCount"],
                         1,
                         enemySpawnBoss=True,
                         bossEnemy="bossSix")
                    musicManager.startBoss("BossSix")

                case _:
                    spawnEnemies(screen, currentRoomID, currentLayerID[0],
                         const.difficultyStats[f"{difficulty}"]["enemyCount"],
                         1,
                         enemySpawnBoss=True,
                         bossEnemy="bossOne")



    #shop logic
    if playerObj.openShop:
        shop.updateShopInstance(layerID=currentLayerID[0])
        playerObj.openShop = False
        result = shop.run(screen,clock,playerObj)
        if result == "quit":
            running = False
        continue

    if currentRoomID == -3 & len(enemyGroup) == 0: musicManager.stopBoss()

    if newRoomID != -3 and len(enemyGroup) > 0:
        musicManager.startCombat()
    else: musicManager.stopCombat()



    pygame.display.flip()

pygame.quit()
