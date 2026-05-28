"""
#ben nethaeyahoo and keyahhno acarkey and emotional support horp
#2026-06-07
#anastasia will write something here
"""

import pygame
import asyncio
import os

import const
from gameHelpers.display import display
import data.gameSaveData.dataSaving as dataSaving

import mapping.tutorial.tutorialGen as tutorial
import mapping.mapLogic.mapGenerator as mapGenerator
from gameHelpers.display.display import spaceCalculator
from   mapping.maps import getEnemySpawns

from   entity.player import player
from   entity.entityClass import enemyBuilder
from   entity.enemyLogic.reader.enemySheetReader import getRandomEnemy

import mainMenu.subMenu.settings as settings
import mainMenu.menu as menu
import mainMenu.subMenu.pauseMenu as pauseMenu

from   gameHelpers.roomDirHelper import getMatchingEntrance, mapDelta, roomIDer,placePlayerAtDoor
from   gameHelpers.mapGeneration import generateEntireWorld
from   gameHelpers.display.dialogueBox import drawDialogueBox

from data.playerUnlockData.playerData.playerDataManager import writeCompendiumEntry
import gameHelpers.display.enemySpawnIndicator as spawner

#pre boot initialization =========================
print(" main: ",settings.loadSettings())
pygame.init()
screen = pygame.display.set_mode(settings.loadSettings()["resolution"])
clock  = pygame.time.Clock()
font   = pygame.font.SysFont(None, 28)
settings.applySettings(settings.loadSettings())
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
playerObj              = player(*screen.get_size(), size=spriteSize)
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


print(settings.loadSettings)







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

if saveDataRead:
    print("main: loading save")
    (
        playerSaveData,
        _,
        currentLayerID,
        weapon,
        roomIDCompendium,
        fullSave,
        difficulty
    ) = saveDataRead

    worldCache = fullSave["worldData"]["layers"]

    #save has full world
    worldGenerated = True
    tutorialFinished = True

    try:
        currentRoomPosX = playerSaveData[1]
        currentRoomPosY = playerSaveData[2]
        playerObj.rect.center = playerSaveData[3]
        if len(weapon) != 0:
            playerObj.getWeapon(
                weapon[0]
            )

    except Exception as e:

        print("main: save load error:", e)

else:
    #tutorial mode=========================
    if currentLayerID[0] == 0:
        generatedMap = tutorial.tutorialMatching[currentLayerID[1]]
        tutorialFinished = False

    #normal game==================================
    else:
        playerObj.allowShoot = True
        playerObj.getWeapon("pistol#1")
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
            asyncio.run(mapGen._generateMap())

            worldCache.setdefault("1", {})["1"] = mapGen.result
            generatedMap    = worldCache["1"]["1"]

        tutorialFinished    = True
        worldGenerated      = False

        if not tutorialFlag:
            worldGenerating = True
            asyncio.run(generateEntireWorld(mapGen, screen, font, worldCache, difficulty))
            worldGenerated  = True
            worldGenerating = False



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
            screenH   = screen.get_height()
        ) #gridH and the other one isnt needed because this works

        enemyGroup.add(enemy)


def spawnEnemies(screen, roomId, layerId, difficulty, enemySpawnOverrideCountPR = None):
    global spawnEffectsStarted
    layout, rowCount, colCount, blockW, blockH = spaceCalculator(screen, roomId)

    if not spawnEffectsStarted:
        print(f"main enemy spawn override count {enemySpawnOverrideCountPR}")

        enemySpawns = getEnemySpawns(roomID=roomId,
                                     layerID=layerId,
                                     difficulty=difficulty,
                                     enemySpawnOverrideCount=enemySpawnOverrideCountPR)
        for row, col in enemySpawns:
            spawnIndicators.append(
                spawner.enemySpawnIndicator(
                    row, col, blockW, blockH,
                    layerID = currentLayerID[0],
                    screenW = screen.get_width(),
                    screenH = screen.get_height(),
                    screen  = screen
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


#main loop====================================

running = True

while running:
    cfg               = settings.loadSettings()
    deltaTime         = clock.tick(cfg["fpsCap"]) / 1000.0
    events            = pygame.event.get()
    winW, winH        = screen.get_size()
    playerObj.screenW = winW
    playerObj.screenH = winH
    keybinds          = cfg.get("keybinds",settings.defaultSettings["keybinds"])

    #event handler====================================
    for event in events:
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            pauseResult = pauseMenu.run(screen,clock)
            if pauseResult == "save":
                dataSaving.saveGameCall(currentLayerID, playerSavePrep, playerObj, worldCache, roomIDCompendium, difficulty)
            elif pauseResult == "menu":
                menuResult, screen = menu.run(screen,clock,font)
                if menuResult == "quit":
                    running = False






            elif pauseResult == "settings":
                result, screen = settings.run( screen, clock, font)
                layout, rowCount, colCount, blockW, blockH = display.spaceCalculator(screen, -1)
                playerObj.size = (blockW * 0.75, blockH * 0.75)
                playerObj.rescaleSprite()
                playerObj.screenH = screen.get_height()
                playerObj.screenW = screen.get_width()
                playerObj.updateSpeed()
                if result == "quit":
                    running = False
            elif pauseResult == "quit":
                running = False


    currentRoomID = generatedMap[currentRoomPosY][currentRoomPosX]
    exitDir = playerObj.touchingExit( currentRoomID)


    #elevator=================================
    if playerObj.touchingElevator(currentRoomID):


        roomIDCompendium = [(0,0)]
        roomIDer(0, 0, roomIDCompendium, True)
        currentRoomPosX = 0
        currentRoomPosY = 0

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
                    asyncio.run(mapGen._generateMap())
                    worldCache.setdefault("1", {})["1"] = mapGen.result
                    generatedMap = worldCache["1"]["1"]


        #normal floors=========================
        else:
            currentLayerID[1]     += 1
            if currentLayerID[1]   > 4:
                currentLayerID[0] += 1
                currentLayerID[1]  = 1

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

    display.drawRoom(screen, generatedMap[currentRoomPosY][currentRoomPosX])

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

    #bullet handler=====================================================================
    for bullet in list(playerObj.bullets):
        for enemy in list(enemyGroup):
            if bullet.rect.colliderect(enemy.rect):
                enemy.takeDamage(bullet.damage)
                bullet.kill()

                if enemy.isDead():
                    enemy.kill()

                break

    #player shot
    for enemy in enemyGroup:
        if enemy.ai is None:
            continue

        for bullet in list(enemy.ai.bullets):
            if bullet.rect.colliderect(playerObj.rect):
                print("main: detected player hit")

                playerObj.takeDamage()

                bullet.kill()

    enemyGroup.update(generatedMap[currentRoomPosY][currentRoomPosX], playerObj, deltaTime)
    for enemy in enemyGroup:
        enemy.draw(screen)

    #tutorial dialogue handling
    if currentLayerID[0] == 0:
        tutorial.runTutorial(screen, tutorial, clock, currentLayerID, currentRoomID,playerObj)
        if currentLayerID[1] == 4 and newRoomID == 33:
            spawnEnemies(screen, currentRoomID, currentLayerID[0], const.difficultyStats[f"{difficulty}"]["enemyCount"],1)
        if currentLayerID[1]==4 and newRoomID == -3:
            spawnEnemies(screen, currentRoomID, currentLayerID[0], const.difficultyStats[f"{difficulty}"]["enemyCount"],3)
    pygame.display.flip()

pygame.quit()