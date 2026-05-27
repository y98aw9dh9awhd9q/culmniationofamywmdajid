"""
#ben nethaeyahoo and keyahhno acarkey and emotional support horp
#2026-06-07
#anastasia will write something here
"""

import pygame
import asyncio

import const
from gameHelpers.display import display
import data.gameSaveData.dataSaving as dataSaving

import mapping.tutorial.tutorialGen as tutorial
import mapping.mapLogic.mapGenerator as mapGenerator

from   entity.player import player

import mainMenu.subMenu.settings as settings
import mainMenu.menu as menu
import mainMenu.subMenu.pauseMenu as pauseMenu

from   gameHelpers.roomDirHelper import getMatchingEntrance, mapDelta, roomIDer,placePlayerAtDoor
from   gameHelpers.mapGeneration import generateEntireWorld
from   gameHelpers.display.dialogueBox import drawDialogueBox

from data.playerUnlockData.playerData.playerDataManager import writeCompendiumEntry

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


#tutorial flags
tutorialDialogueFirst  = True
tutorialDialogueSecond = True
tutorialDialogue2x     = True
tutorialDialogueArrow  = True




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

                if roomIDResult == "NEW" and newRoomID > 0:
                    playerObj.doorsLocked = True
                    print("room locked")

            except Exception as e:
                print("main:no room id", e)

    if transitionCooldown > 0:
        transitionCooldown -= deltaTime


    #render========================================




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

    #tutorial dialogue handling
    if currentLayerID[0] == 0:

        #tutorial first
        if currentRoomID == 12 and currentLayerID == [0,1]:
            if tutorialDialogueFirst:
                    finishedDial = drawDialogueBox(screen,tutorial.tutorialDialogueFirst , clock,typewrite=True)
                    if finishedDial:
                        tutorialDialogueFirst = False
                        playerObj.doorsLocked = False


        #tutorial floor 2
        if currentLayerID[1] == 2:
            if currentRoomID == -7:
                if tutorialDialogueSecond:
                    playerObj.doorsLocked = True
                    finishedDial = drawDialogueBox(screen,tutorial.tutorialDialogueSecond , clock,typewrite=True)
                    if finishedDial:
                        tutorialDialogueSecond = False
                        playerObj.doorsLocked = False

            if currentRoomID == -8:
                if tutorialDialogue2x:
                    playerObj.doorsLocked = True
                    finishedDial = drawDialogueBox(screen,tutorial.tutorialDialogueSecondSecond , clock,typewrite=True)
                    if finishedDial:
                        tutorialDialogue2x = False
                        playerObj.doorsLocked = False

        if currentLayerID[1] == 3:
            if currentRoomID == -9:
                if tutorialDialogueArrow:
                    playerObj.doorsLocked = True
                    finishedDial = drawDialogueBox(screen,tutorial.tutorialArrowRoom , clock,typewrite=True)
                    if finishedDial:
                        tutorialDialogueArrow = False
                        playerObj.doorsLocked = False



    pygame.display.flip()

pygame.quit()