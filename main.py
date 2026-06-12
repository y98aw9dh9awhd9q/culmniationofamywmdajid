"""
#ben nethaeyahoo and keyahhno acarkey and emotional support horp
#2026-06-07
The Amazing Digital Dungeon!

This is a game inspired by games such as but not limited to:
Enter The Gungeon,
most importantly: Touhou, Calamity Mod, The Amazing Digital Circus,
etc.

This game features a tutorial and interactive menus. The main gameplay is going through 6 layers
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
import gameHelpers.menus
import gameHelpers.networkState as networkState


from   gameHelpers.roomDirHelper      import getMatchingEntrance, mapDelta, roomIDer,placePlayerAtDoor
from   gameHelpers.mapGeneration      import generateEntireWorld
from   gameHelpers.display.hud        import drawHud, drawGameOver, drawWinScreen
from   gameHelpers.display.display    import spaceCalculator
from   gameHelpers.musMan             import musManager

from data.playerUnlockData.playerData.playerDataManager import writeCompendiumEntry
import gameHelpers.display.enemySpawnIndicator as spawner

from   data.playerUnlockData.playerData.playerDataManager import addEnemyKill

from   entity.weapons.bullet          import bullet
from   mapping.maps import getWallRects, getBreakableRectsWithCoords, breakTile, roomRegistery

screen             = None
clock              = None
font               = None
playerObj          = None
mapGen             = None
generatedMap       = None
currentRoomPosY    = 0
currentRoomPosX    = 0
transitionCooldown = 0.0
playerSavePrep     = None
worldCache         = None
tutorialFinished   = False
worldGenerated     = False
worldGenerating    = False
roomIDCompendium   = None
gameOver           = False
gameOverTimer      = 0.0
gameWin            = False
gameWinTimer       = 0.0
newRoomID          = 0
currentLayerID     = None
difficulty         = None
tutorialFlag       = None
deathCount         = 0
musicManager       = None
enemyGroup         = None
playerSpriteGroup  = None
spawnIndicators    = None
spawnEffectsStarted = False
running            = False
loadedSettings     = None
remotePlayers      = {}
localPlayerDead    = False
prShopBusyFor      = set()
prBossScaled       = False
clientEnemyImgCache= {}

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


async def resetRun():
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

    menuRes = await gameHelpers.menus.mainMenu(screen, clock, font)

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
        await mapGen.prGenerateMap()
        worldCache = {
            "1": {
                "1": mapGen.result
            }
        }

        generatedMap    = worldCache["1"]["1"]
        worldGenerating = True
        await generateEntireWorld(mapGen, screen, font, worldCache, difficulty)
        worldGenerated  = True
        worldGenerating = False

    tutorial.resetTutorial()

    currentRoomPosX = 0
    currentRoomPosY = 0
    dataSaving.deleteSave()
    resetSpawnEffects()

    print("main: run reset complete")


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
            enemyName  = getRandomEnemy(layerID[0]),
            spawnPos   = (enemyX, enemyY),
            layer      = layerID[0],
            screenW    = screen.get_width(),
            screenH    = screen.get_height(),
            difficulty = difficulty
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
                        layerID    = currentLayerID[0],
                        screenW    = screen.get_width(),
                        screenH    = screen.get_height(),
                        screen     = screen,
                        difficulty = difficulty,
                    )
                )
        else:
            spawnIndicators.append(
                spawner.enemySpawnIndicator(
                    rowB, colB, blockW, blockH,
                    layerID      = 6767,
                    screenW      = screen.get_width(),
                    screenH      = screen.get_height(),
                    screen       = screen,
                    difficulty   = difficulty,
                    forcedEnemy  = bossEnemy,
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


async def prClientMode():
    global running, gameOver, gameOverTimer, gameWin, gameWinTimer
    global currentRoomID, currentRoomPosX, currentRoomPosY
    global enemyGroup, spawnIndicators, remotePlayers
    global generatedMap, localPlayerDead, screen

    generatedMap      = None
    worldState        = None
    prShopSent        = False
    prShopBuys        = []
    prPendingBullets  = []
    prPendingShop     = False
    prPendingShopBuys = None

    while running:
        await asyncio.sleep(0)

        cfg               = settings.loadSettings()
        deltaTime         = clock.tick(cfg["fpsCap"]) / 1000.0
        events            = pygame.event.get()
        winW, winH        = screen.get_size()
        playerObj.screenW = winW
        playerObj.screenH = winH
        keybinds          = cfg.get("keybinds", settings.defaultSettings["keybinds"])

        #events ====================================
        for event in events:
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pauseResult = pauseMenu.run(screen, clock)
                if pauseResult in ("menu", "quit"):
                    running = False
                elif pauseResult == "settings":
                    result, screen       = settings.run(screen, clock, font)
                    playerObj.size       = (int(winW / 15 * 0.75),
                                            int(winH / 9 * 0.75))
                    playerObj.rescaleSprite()
                    display.setAssets(screen)
                    if result == "quit":
                        running = False

        if gameOver:
            screen.fill((0, 0, 0))
            drawGameOver(screen)
            gameOverTimer -= deltaTime
            pygame.display.flip()
            for event in events:
                if event.type    == pygame.QUIT:
                    running       = False
                if event.type    == pygame.KEYDOWN and event.key == keybinds["interact"]:
                    gameOverTimer = 0
                if event.type    == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    gameOverTimer = 0
            if gameOverTimer     <= 0:
                running = False
            continue

        if gameWin:
            screen.fill((0, 0, 0))
            drawWinScreen(screen)
            gameWinTimer        -= deltaTime
            pygame.display.flip()
            for event in events:
                if event.type   == pygame.QUIT:
                    running      = False
                if event.type   == pygame.KEYDOWN and event.key == keybinds["interact"]:
                    gameWinTimer = 0
                if event.type   == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    gameWinTimer = 0
            if gameWinTimer     <= 0:
                running          = False
            continue

        #bullet tracker
        currentRoomID            = worldState.get("roomId", -1) if worldState else -1

        if not localPlayerDead:
            playerObj.bullets.empty()

            playerObj.update(
                deltaTime, currentRoomID, currentLayerID,
                currentRoomPosX, currentRoomPosY, keybinds
            )

            newBulletCount       = len(playerObj.bullets)
            if newBulletCount > 0:
                for b in list(playerObj.bullets):
                    vLen = b.velocity.length()
                    if vLen > 0:
                        dx = b.velocity.x / vLen
                        dy = b.velocity.y / vLen
                    else:
                        dx, dy = 0, 0
                    prPendingBullets.append((dx, dy))




            if playerObj.openShop and not prShopSent:
                playerObj.openShop = False
                prShopSent         = True
                prPendingShop      = True
                shop.updateShopInstance(layerID=currentLayerID[0])
                prShopBuys.clear()
                def prOnBuy(itemIdx):
                    prShopBuys.append(itemIdx)
                shop.run(screen, clock, playerObj, onBuy=prOnBuy)

                if prShopBuys:
                    prPendingShopBuys = list(prShopBuys)
                    prShopBuys.clear()
            elif not playerObj.openShop:
                prShopSent = False

        try:
            prSendMsg = {"type": "playerState", "x": playerObj.posX, "y": playerObj.posY}
            if prPendingBullets:
                prSendMsg["bullets"]      = prPendingBullets
                prPendingBullets          = []
            if prPendingShop:
                prSendMsg["shopInteract"] = True
                prPendingShop             = False
            if prPendingShopBuys:
                prSendMsg["shopBuys"]     = prPendingShopBuys
                prPendingShopBuys         = None
            await networkState.client.send(prSendMsg)
        except Exception:
            pass




        try:
            msgs                = await networkState.client.getMessages()
            for msg in msgs:
                if msg["type"] == "worldState":
                    worldState  = msg
        except Exception:
            pass

        if worldState is None:
            screen.fill((0, 0, 0))
            ww, wh       = screen.get_size()
            waitText     = font.render("waiting for host...", True, (180, 180, 180))
            screen.blit(waitText, (ww // 2 - waitText.get_width() // 2,
                                   wh // 2 - waitText.get_height() // 2))
            pygame.display.flip()
            continue

        prevRoomID               = currentRoomID
        currentRoomID            = worldState["roomId"]
        currentRoomPosX          = worldState["roomPosX"]
        currentRoomPosY          = worldState["roomPosY"]
        playerObj.doorsLocked    = worldState["doorsLocked"]
        myId                     = getattr(networkState.client, "playerId", None)
        allPlayerData            = worldState.get("players", [])
        localPlayerDead          = False

        for p in allPlayerData:
            if p["id"]              == myId:
                playerObj.hp         = p.get("hp", playerObj.hp)
                playerObj.maxHp      = p.get("maxHp", playerObj.maxHp)
                playerObj.money      = p.get("money", playerObj.money)
                playerObj.inventory  = p.get("inventory", playerObj.inventory)
                if p.get("dead", False):
                    playerObj.hp     = 0
                    localPlayerDead  = True
                if currentRoomID    != prevRoomID:
                    playerObj.posX   = p.get("x", playerObj.posX)
                    playerObj.posY   = p.get("y", playerObj.posY)
                    playerObj.rect.x = playerObj.posX
                    playerObj.rect.y = playerObj.posY
                break

        #sync all players
        for p in allPlayerData:
            if p["id"] == myId:
                continue
            cid = p["id"]
            if cid not in remotePlayers:
                remotePlayers[cid] = {
                    "obj": player(*screen.get_size(),
                                 size=playerObj.size, screen=screen),
                    "dead": False
                }
            rp = remotePlayers[cid]
            rp["dead"] = p.get("dead", False)
            rpObj = rp["obj"]
            rpObj.rect.x = p["x"]
            rpObj.rect.y = p["y"]
            rpObj.posX   = p["x"]
            rpObj.posY   = p["y"]
            rpObj.hp     = p.get("hp", 6)
            rpObj.maxHp  = p.get("maxHp", 6)

        gameOver                 = worldState.get("gameOver", False)
        gameWin                  = worldState.get("gameWin", False)
        if gameOver:
            gameOverTimer        = 30

        #sync brokens
        remaining = set(tuple(p) for p in worldState.get("remainingBreakables", []))
        for rect, rowIdx, colIdx in getBreakableRectsWithCoords(currentRoomID, winW, winH):
            if (rowIdx, colIdx) not in remaining:
                breakTile(currentRoomID, rowIdx, colIdx)

        #render
        screen.fill((0, 0, 0))
        display.drawRoom(screen, currentRoomID, playerObj.doorsLocked)

        #draw all players
        for rp in remotePlayers.values():
            if not rp["dead"]:
                display.drawPlayer(screen, rp["obj"])

        #draw enemies via state
        prEW, prEH = int(winW / 15 * 0.75), int(winH / 9 * 0.75)
        for e in worldState.get("enemies", []):
            name                 = e.get("name", "")
            if name not in clientEnemyImgCache:
                imgPath = const.enemyPths.get(name)
                if imgPath:
                    try:
                        img = pygame.image.load(imgPath).convert_alpha()
                        img = pygame.transform.scale(img, (prEW, prEH))
                        clientEnemyImgCache[name] = img
                    except Exception:
                        clientEnemyImgCache[name] = None

                else:
                    clientEnemyImgCache[name]     = None
            cached                                = clientEnemyImgCache.get(name)

            if cached is not None:
                screen.blit(cached, (e["x"], e["y"]))
            else:
                isBoss = "boss" in name.lower()
                color  = (255, 200, 0) if isBoss else (200, 60, 60)
                pygame.draw.rect(screen, color,
                                 (e["x"], e["y"], prEW, prEH))

        #draw boss bar from world state
        for e in worldState.get("enemies", []):
            if e.get("name", "").lower().startswith("boss"):
                barW          = int(winW * 0.58)
                barH          = 18
                bx            = (winW - barW) // 2
                by            = 18
                fillRatio     = max(0.0, min(1.0, e["hp"] / e["maxHp"])) if e["maxHp"] > 0 else 0
                pygame.draw.rect(screen, (25, 20, 20), (bx, by, barW, barH))
                pygame.draw.rect(screen, (210, 35, 55), (bx, by, int(barW * fillRatio), barH))
                pygame.draw.rect(screen, const.white, (bx, by, barW, barH), 2)
                bossLabel     = font.render(e.get("phaseName", "BOSS"), True, const.white)
                screen.blit(bossLabel, (winW // 2 - bossLabel.get_width() // 2, by + barH + 13))
                break

        for b in worldState.get("bullets", []):
            color              = tuple(b["color"])
            bw                 = b.get("w", 8)
            bh                 = b.get("h", 8)
            pygame.draw.rect(screen, color,
                             (b["x"] - bw // 2, b["y"] - bh // 2, bw, bh))

        prBeamSurf = None
        for beam in worldState.get("beams", []):
            sx, sy = beam.get("x1", 0), beam.get("y1", 0)
            ex, ey = beam.get("x2", 0), beam.get("y2", 0)
            if sx == ex and sy == ey:
                continue
            if prBeamSurf is None:
                prBeamSurf = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
            pygame.draw.line(prBeamSurf, (255, 80, 40, 160), (sx, sy), (ex, ey), 6)
            pygame.draw.line(prBeamSurf, (255, 150, 80), (sx, sy), (ex, ey), 3)
        if prBeamSurf is not None:
            screen.blit(prBeamSurf, (0, 0))

        if not localPlayerDead:
            display.drawPlayer(screen, playerObj)

        drawHud(
            screen,
            playerObj,
            generatedMap,
            currentRoomPosY,
            currentRoomPosX,
            roomIDCompendium,
        )

        pygame.display.flip()


async def mainAsync():
    global screen, clock, font, running
    global playerObj, mapGen, generatedMap, currentRoomPosY, currentRoomPosX
    global transitionCooldown, playerSavePrep, worldCache
    global tutorialFinished, worldGenerated, worldGenerating, roomIDCompendium
    global gameOver, gameOverTimer, gameWin, gameWinTimer, newRoomID
    global currentLayerID, difficulty, tutorialFlag, deathCount
    global remotePlayers, localPlayerDead, prBossScaled
    global musicManager, enemyGroup, playerSpriteGroup
    global spawnIndicators, spawnEffectsStarted, loadedSettings
    #yep, this is a fail, too many globals - nagra probably

    #pre boot initialization =========================
    print(" main: ", settings.loadSettings())
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
    menuRes = await gameHelpers.menus.mainMenu(screen, clock, font)

    tutorialFlag       = menuRes[1]
    difficulty         = menuRes[0]

    print(f"main recieved menu result {menuRes}")
    cfg                = settings.loadSettings()
    screen             = settings.applySettings(cfg)
    loadedSettings     = settings.loadSettings()

    #core vars ===================================
    layout, rowCount, colCount, blockW, blockH = display.spaceCalculator(screen, -1)

    spriteH, spriteW       = blockH * 0.75, blockW * 0.75
    spriteSize             = (spriteW, spriteH)
    playerObj              = player(*screen.get_size(), size=spriteSize, screen=screen)
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

    musicManager.registerTrack("combat", "assets/music/sanctuary.mp3")

    #musicManager.registerTrack("shop","assets/music/shop.mp3") NYI

    musicManager.registerTrack("bossBossOne",   "assets/music/antiHeroSwaft.mp3")
    musicManager.registerTrack("bossBossTwo",   "assets/music/ROTJD.mp3")
    musicManager.registerTrack("bossBossThree", "assets/music/slimeGob.mp3")
    musicManager.registerTrack("bossBossFour",  "assets/music/farowl.mp3")
    musicManager.registerTrack("bossBossFive",  "assets/music/SIOSwaft.mp3")
    musicManager.registerTrack("bossBossSix",   "assets/music/farowl.mp3")

    #current floor logic===========================

    if tutorialFlag:
        print("main: tutorial started")
        currentLayerID = [0, 1]
    else:
        print("main: normal layer")
        currentLayerID = [1, 1]

    #sprite groups===========================

    playerSpriteGroup    = pygame.sprite.Group()
    playerSpriteGroup.add(playerObj)
    enemyGroup           = pygame.sprite.Group()

    #multiplayer init===================================
    if networkState.isMultiplayer:
        playerObj.allowShoot = True
        playerObj.getWeapon("basicPistol")
        playerObj.money      = 0
        playerObj.difficulty = difficulty

        if networkState.isHost:
            dataSaving.deleteSave()

        else:
            #client skips world gen
            running = True
            await prClientMode()
            running = False

            if networkState.client:
                await networkState.client.disconnect()
                networkState.client = None
            networkState.isMultiplayer = False
            networkState.isHost   = False
            remotePlayers.clear()
            localPlayerDead = False
            await resetRun()

    #save loader=======================
    saveDataRead = dataSaving.readSave()
    if "1" not in worldCache or "1" not in worldCache.get("1", {}):
        mapGen.size = 3
        mapGen.setupMap(boss=False)
        await mapGen.prGenerateMap()
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
        worldGenerated   = True
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
            generatedMap      = tutorial.tutorialMatching[currentLayerID[1]]
            tutorialFinished  = False

        #normal game==================================
        else:
            playerObj.allowShoot = True
            playerObj.getWeapon("basicPistol")
            mapGen.size = 3
            mapGen.setupMap(boss=False)
            await mapGen.prGenerateMap()

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
                await mapGen.prGenerateMap()

                worldCache.setdefault("1", {})["1"] = mapGen.result
                generatedMap = worldCache["1"]["1"]

            tutorialFinished   = True
            worldGenerated     = False

            if not tutorialFlag:
                worldGenerating = True
                await generateEntireWorld(mapGen, screen, font, worldCache, difficulty)
                worldGenerated  = True
                worldGenerating = False

            dataSaving.saveGameCall(currentLayerID, playerSavePrep, playerObj, worldCache, roomIDCompendium, difficulty)

    #load first
    if currentLayerID[0] == 0:
        generatedMap = tutorial.tutorialMatching[currentLayerID[1]]
    else:
        print(worldCache)
        generatedMap = worldCache[str(currentLayerID[0])][str(currentLayerID[1])]

    #main loop====================================

    running = True

    while running:
        await asyncio.sleep(0)

        if len(enemyGroup) == 0:
            playerObj.doorsLocked = False
        elif len(enemyGroup) > 0:
            playerObj.doorsLocked = True

        cfg               = settings.loadSettings()
        deltaTime         = clock.tick(cfg["fpsCap"]) / 1000.0
        events            = pygame.event.get()
        winW, winH        = screen.get_size()
        playerObj.screenW = winW
        playerObj.screenH = winH
        keybinds          = cfg.get("keybinds", settings.defaultSettings["keybinds"])

        if gameOver:
            print("main: game over logic run")
            screen.fill((0, 0, 0))
            drawGameOver(screen)
            gameOverTimer -= deltaTime
            pygame.display.flip()

            for event in events:
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN and event.key == loadedSettings["keybinds"]["interact"]:
                    gameOverTimer = 0
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    gameOverTimer = 0

            #notify clients of game over
            if networkState.isMultiplayer and networkState.isHost:
                prPlayers = [{"id": 0, "x": playerObj.posX, "y": playerObj.posY,
                              "hp": playerObj.hp, "maxHp": playerObj.maxHp,
                              "dead": localPlayerDead}]
                for cid, rp in remotePlayers.items():
                    prPlayers.append({"id": cid, "x": rp["obj"].posX, "y": rp["obj"].posY,
                                      "hp": rp["obj"].hp, "maxHp": rp["obj"].maxHp,
                                      "dead": rp["dead"]})
                await networkState.server.broadcast({
                    "type":        "worldState",
                    "roomId":      currentRoomID,
                    "roomPosX":    currentRoomPosX,
                    "roomPosY":    currentRoomPosY,
                    "doorsLocked": playerObj.doorsLocked,
                    "players":     prPlayers,
                    "enemies":     [],
                    "bullets":     [],
                    "gameOver":    True,
                    "gameWin":     False,
                })

            if gameOverTimer <= 0:
                if networkState.isMultiplayer:
                    if networkState.server:
                        await networkState.server.stop()
                    if networkState.client:
                        await networkState.client.disconnect()
                    networkState.server = None
                    networkState.client = None
                    networkState.isMultiplayer = False
                    networkState.isHost   = False
                    remotePlayers.clear()
                    localPlayerDead = False
                    await resetRun()
                else:
                    await resetRun()

            continue

        if gameWin:
            screen.fill((0, 0, 0))
            drawWinScreen(screen)
            gameWinTimer -= deltaTime
            pygame.display.flip()

            #ensure everyone knows the game is won
            if networkState.isMultiplayer and networkState.isHost:
                prPlayers = [{"id": 0, "x": playerObj.posX, "y": playerObj.posY,
                              "hp": playerObj.hp, "maxHp": playerObj.maxHp,
                              "dead": localPlayerDead}]
                for cid, rp in remotePlayers.items():
                    prPlayers.append({"id": cid, "x": rp["obj"].posX, "y": rp["obj"].posY,
                                      "hp": rp["obj"].hp, "maxHp": rp["obj"].maxHp,
                                      "dead": rp["dead"]})

                await networkState.server.broadcast({
                    "type":        "worldState",
                    "roomId":      currentRoomID,
                    "roomPosX":    currentRoomPosX,
                    "roomPosY":    currentRoomPosY,
                    "doorsLocked": playerObj.doorsLocked,
                    "players":     prPlayers,
                    "enemies":     [],
                    "bullets":     [],
                    "gameOver":    False,
                    "gameWin":     True,
                })

            for event in events:
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN and event.key == loadedSettings["keybinds"]["interact"]:
                    gameWinTimer = 0
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    gameWinTimer = 0

            if gameWinTimer <= 0:
                if networkState.isMultiplayer:
                    if networkState.server:
                        await networkState.server.stop()
                    if networkState.client:
                        await networkState.client.disconnect()
                    networkState.server        = None
                    networkState.client        = None
                    networkState.isMultiplayer = False
                    networkState.isHost        = False
                    remotePlayers.clear()
                    localPlayerDead            = False
                    await resetRun()
                else:
                    await resetRun()

            continue

        #event handler====================================
        for event in events:
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pauseResult = pauseMenu.run(screen, clock)
                if pauseResult == "save" and not networkState.isMultiplayer:
                    print("main: save game called")
                    dataSaving.saveGameCall(currentLayerID, playerSavePrep, playerObj, worldCache, roomIDCompendium, difficulty)
                elif pauseResult == "menu":
                    if networkState.isMultiplayer:
                        if networkState.server:
                            await networkState.server.stop()
                        if networkState.client:
                            await networkState.client.disconnect()
                        networkState.server = None
                        networkState.client = None
                        networkState.isMultiplayer = False
                        networkState.isHost   = False
                        remotePlayers.clear()
                        localPlayerDead = False
                        await resetRun()
                    else:
                        menuResult, screen = menu.run(screen, clock, font)

                        if type(menuResult) == tuple:
                            await resetRun()

                        match menuResult:
                            case "quit": running = False

                            case "infiniteHp":
                                playerObj.hp     = 6767
                                playerObj.maxHp  = 6767

                            case "allGuns":
                                for gun in playerObj.gunList:
                                    playerObj.getWeapon(gun)


                            case "infiniteHeals":
                                for _ in range(1000):
                                    playerObj.getItem("HP1")

                            case "teleportToBoss":
                                currentLayerID[1] = 4
                                generatedMap      = worldCache[str(currentLayerID[0])][str(currentLayerID[1])]
                                mapSize           = len(generatedMap)
                                currentRoomPosY   = mapSize - 1
                                currentRoomPosX   = mapSize - 2
                                newRoomID         = -3
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
                                if not networkState.isMultiplayer:
                                    dataSaving.saveGameCall(currentLayerID, playerSavePrep, playerObj, worldCache, roomIDCompendium, difficulty)

                elif pauseResult == "settings":
                    result, screen = settings.run(screen, clock, font)
                    layout, rowCount, colCount, blockW, blockH = display.spaceCalculator(screen, -1)
                    playerObj.size   = (blockW * 0.75, blockH * 0.75)
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
            currentRoomID   = -1
        except Exception as e:
            print(f"main: error caught in room ID process {e}")

        #use first alive player for room movement
        exitDir = playerObj.touchingExit(currentRoomID)
        if localPlayerDead:
            for rp in remotePlayers.values():
                if not rp["dead"]:
                    exitDir = rp["obj"].touchingExit(currentRoomID)
                    break

        #elevator=================================
        prElevatorTouch = playerObj.touchingElevator(currentRoomID)
        if localPlayerDead:
            for rp in remotePlayers.values():
                if not rp["dead"]:
                    prElevatorTouch = rp["obj"].touchingElevator(currentRoomID)
                    break
        if prElevatorTouch:
            if currentLayerID == [6, 4]:
                if not networkState.isMultiplayer:
                    dataSaving.deleteSave()
                gameWin      = True
                gameWinTimer = 8
                musicManager.stopAll()
                continue

            #revive dead players at elevator=================
            if networkState.isMultiplayer:
                #looks for an alive player's hp for revials
                prAliveHp = playerObj.hp
                if localPlayerDead:
                    for rp in remotePlayers.values():
                        if not rp["dead"]:
                            prAliveHp = rp["obj"].hp
                            break
                if localPlayerDead:
                    localPlayerDead = False
                    playerObj.hp    = prAliveHp
                    playerObj.invincibilityTimer = playerObj.immuFrameTime
                    print(f"main: host revived with {prAliveHp} HP")
                for cid, rp in remotePlayers.items():
                    if rp["dead"]:
                        rp["dead"]    = False
                        rp["obj"].hp = prAliveHp
                        rp["obj"].invincibilityTimer = rp["obj"].immuFrameTime
                        print(f"main: client {cid} revived with {prAliveHp} HP")

            resetAllRooms()
            shopInstance.resetStock()
            if not networkState.isMultiplayer:
                dataSaving.saveGameCall(currentLayerID, playerSavePrep, playerObj, worldCache, roomIDCompendium, difficulty)

            roomIDCompendium = [(0, 0)]
            roomIDer(0, 0, roomIDCompendium, True)
            currentRoomPosX  = 0
            currentRoomPosY  = 0

            if networkState.isMultiplayer and networkState.isHost:
                for rp in remotePlayers.values():
                    rp["obj"].rect.center = (winW // 2, winH // 2)
                    rp["obj"].syncPos()
                    for bulletSprite in rp["obj"].bullets:
                        bulletSprite.kill()

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
                    tutorialFinished  = True
                    currentLayerID[0] = 1
                    currentLayerID[1] = 1
                    writeCompendiumEntry("achievements", "tutorial")
                    currentRoomPosX   = 0
                    currentRoomPosY   = 0

                    # generate full world========================
                    if not worldGenerated:
                        worldGenerating = True
                        await generateEntireWorld(mapGen, screen, font, worldCache, difficulty)
                        worldGenerated  = True
                        worldGenerating = False

                    print(worldCache)
                    try:
                        generatedMap = worldCache["1"]["1"]
                    except KeyError:
                        print("main: world cache missing 1-1")

                        mapGen.size = 3
                        mapGen.setupMap(boss=False)
                        await mapGen.prGenerateMap()
                        worldCache.setdefault("1", {})["1"] = mapGen.result
                        generatedMap = worldCache["1"]["1"]

            #normal floors=========================
            else:
                currentLayerID[1] += 1
                if currentLayerID[1] > 4:
                    playerObj.increaseMaxHP()
                    currentLayerID[0] += 1
                    currentLayerID[1]  = 1
                    if currentLayerID[0] % 2 != 0:
                        playerObj.increaseHeal()

                if currentLayerID[0] > 9:
                    currentLayerID[0] = 9
                    currentLayerID[1] = 4

                generatedMap = worldCache[str(currentLayerID[0])][str(currentLayerID[1])]

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
                    placePlayerAtDoor(playerObj, doorRect, exitDir)

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

                #teleport all remote players with host
                if networkState.isMultiplayer and networkState.isHost and doorRect:
                    for rp in remotePlayers.values():
                        placePlayerAtDoor(rp["obj"], doorRect, exitDir)
                        rp["obj"].syncPos()
                        for bulletSprite in rp["obj"].bullets:
                            bulletSprite.kill()

                try:
                    print(f"main: new room id {newRoomID}")
                    print(f"main:current layeriD: {currentLayerID}spawns: {const.enemySpawnCount(currentLayerID[0], 1)}")

                    if roomIDResult == "NEW" and (newRoomID > 0 or newRoomID == -3):
                        playerObj.doorsLocked = True
                        spawnEffectsStarted   = False
                        print("room locked")

                except Exception as e:
                    print("main:no room id", e)

        if transitionCooldown > 0:
            transitionCooldown -= deltaTime

        #render=======================================

        screen.fill((0, 0, 0))

        display.drawRoom(screen, generatedMap[currentRoomPosY][currentRoomPosX], playerObj.doorsLocked)

        if not localPlayerDead:
            playerObj.update(
                deltaTime,
                generatedMap[currentRoomPosY][currentRoomPosX],
                currentLayerID,
                currentRoomPosX,
                currentRoomPosY,
                keybinds
            )

        #host message handler=========================
        if networkState.isMultiplayer and networkState.isHost:
            msgs = await networkState.server.getMessages()
            for msg in msgs:
                cid = msg.get("prFrom")
                if cid is None:
                    continue
                if cid not in remotePlayers:
                    remotePlayers[cid] = {
                        "obj": player(*screen.get_size(),
                                      size=spriteSize, screen=screen),
                        "dead": False
                    }
                rp = remotePlayers[cid]
                rpObj = rp["obj"]
                if msg["type"] == "playerState":
                    rpObj.rect.x  = msg["x"]
                    rpObj.rect.y  = msg["y"]
                    rpObj.posX    = msg["x"]
                    rpObj.posY    = msg["y"]
                    for dx, dy in msg.get("bullets", []):
                        tx = rpObj.rect.centerx + dx * 10000
                        ty = rpObj.rect.centery + dy * 10000
                        newB  = bullet(
                            rpObj.rect.centerx,
                            rpObj.rect.centery,
                            tx, ty,
                            (screen.get_width(), screen.get_height()),
                            owner=cid,
                            difficulty=difficulty,
                        )
                        rpObj.bullets.add(newB)
                    for itemIndex in msg.get("shopBuys", []):
                        shop.updateShopInstance(layerID=currentLayerID[0])
                        shopInstance.buy(rpObj, itemIndex)

            #update timers for all remote players
            for rp in remotePlayers.values():
                rpObj = rp["obj"]
                if rpObj.invincibilityTimer > 0:
                    rpObj.invincibilityTimer -= deltaTime
                if rpObj.dodgeCooldownTimer > 0:
                    rpObj.dodgeCooldownTimer -= deltaTime
                if rpObj.shootTimer > 0:
                    rpObj.shootTimer -= deltaTime
                if rpObj.invertedControlsTimer > 0:
                    rpObj.invertedControlsTimer -= deltaTime

            wallRects = getWallRects(currentRoomID, winW, winH)
            breakableData  = getBreakableRectsWithCoords(currentRoomID, winW, winH)
            def prOnBreak(rowIdx, colIdx):
                breakTile(currentRoomID, rowIdx, colIdx)
            for rp in remotePlayers.values():
                for b in list(rp["obj"].bullets):
                    b.update(deltaTime, winW, winH,
                             wallRects=wallRects,
                             breakableData=breakableData,
                             onBreak=prOnBreak)

        #draw player bullets
        playerObj.bullets.draw(screen)

        #draw remote bullets
        if networkState.isMultiplayer and networkState.isHost:
            for rp in remotePlayers.values():
                if not rp["dead"]:
                    display.drawPlayer(screen, rp["obj"])
                    rp["obj"].bullets.draw(screen)

        if not localPlayerDead:
            display.drawPlayer(screen, playerObj)

        drawHud(
            screen,
            playerObj,
            generatedMap,
            currentRoomPosY,
            currentRoomPosX,
            roomIDCompendium,
        )

        #bullet handler=====================================================================
        prBulletsToCheck = list(playerObj.bullets)
        if networkState.isMultiplayer and networkState.isHost:
            for rp in remotePlayers.values():
                prBulletsToCheck += list(rp["obj"].bullets)

        for prBlt in prBulletsToCheck:
            for enemy in list(enemyGroup):

                if enemy.ai and hasattr(enemy.ai, "shieldBlocksBullet"):
                    if enemy.ai.shieldBlocksBullet(prBlt):
                        prBlt.kill()
                        break

                if prBlt.rect.colliderect(enemy.rect):
                    enemy.takeDamage(prBlt.damage)
                    prBlt.kill()

                    if enemy.isDead():
                        addEnemyKill(enemy.enemyName)
                        enemy.kill()
                        prKillMoney = 1 + (2 * currentLayerID[0])
                        playerObj.money += prKillMoney
                        if networkState.isMultiplayer:
                            for rp in remotePlayers.values():
                                rp["obj"].money += prKillMoney

                    break

        #check if all dead
        def prAllDead():
            if not localPlayerDead:
                return False
            for rp in remotePlayers.values():
                if not rp["dead"]:
                    return False
            return True

        def prTriggerGameOver():
            global gameOver, gameOverTimer
            gameOver      = True
            gameOverTimer = 30
            deleteCurrentProgress()
            enemyGroup.empty()
            for bulletSprite in playerObj.bullets:
                bulletSprite.kill()
            for rp in remotePlayers.values():
                for bulletSprite in rp["obj"].bullets:
                    bulletSprite.kill()
            print("main: all players died")

        #player shot =====================================
        for enemy in enemyGroup:
            if enemy.ai is None:
                continue

            if hasattr(enemy.ai, "beamHitsPlayer"):
                if enemy.ai.beamHitsPlayer(playerObj):
                    print("main: detected beam hits player")
                    playerObj.takeDamage(enemy.atk)
                    if playerObj.hp    <= 0:
                        localPlayerDead = True
                    if prAllDead() and not gameOver:
                        prTriggerGameOver()

                if networkState.isMultiplayer and networkState.isHost:
                    for rp in remotePlayers.values():
                        if rp["dead"]:
                            continue
                        rpObj              = rp["obj"]
                        if enemy.ai.beamHitsPlayer(rpObj):
                            rpObj.takeDamage(enemy.atk)
                            if rpObj.hp   <= 0:
                                rp["dead"] = True
                            if prAllDead() and not gameOver:
                                prTriggerGameOver()

            for prEnemyBlt in list(enemy.ai.bullets):
                #bullet vs host
                if prEnemyBlt.rect.colliderect(playerObj.rect):
                    print("main: detected player hit")
                    playerObj.takeDamage(prEnemyBlt.damage)
                    prEnemyBlt.kill()
                    if playerObj.hp <= 0:
                        localPlayerDead = True
                    if prAllDead() and not gameOver:
                        prTriggerGameOver()
                    continue

                #bullet vs remote
                if networkState.isMultiplayer and networkState.isHost:
                    for rp in remotePlayers.values():
                        if rp["dead"]:
                            continue
                        rpObj = rp["obj"]
                        if prEnemyBlt.rect.colliderect(rpObj.rect):
                            prEnemyBlt.kill()
                            rpObj.takeDamage(prEnemyBlt.damage)
                            if rpObj.hp <= 0:
                                rp["dead"] = True
                            if prAllDead() and not gameOver:
                                prTriggerGameOver()
                            break

        #targets first alive player (usually the remote player)
        prTargetObj = playerObj
        if networkState.isMultiplayer:
            for rp in remotePlayers.values():
                if not rp["dead"]:
                    prTargetObj = rp["obj"]
                    break
        enemyGroup.update(generatedMap[currentRoomPosY][currentRoomPosX], prTargetObj, deltaTime)
        for enemy in enemyGroup:
            enemy.draw(screen)
        drawBossBar(screen, enemyGroup, font)

        #tutorial special case enemy spawns
        if currentLayerID[0] == 0:
            tutorial.runTutorial(screen, clock, currentLayerID, currentRoomID, playerObj)
            if currentLayerID[1] == 4 and newRoomID == 33:
                spawnEnemies(screen, currentRoomID, currentLayerID[0], const.difficultyStats[f"{difficulty}"]["enemyCount"], 1)
            if currentLayerID[1] == 4 and newRoomID == -3:
                spawnEnemies(screen, currentRoomID, currentLayerID[0], const.difficultyStats[f"{difficulty}"]["enemyCount"], 3)

        else:
            if newRoomID > 0:
                spawnEnemies(screen, newRoomID, currentLayerID[0], const.difficultyStats[difficulty]["enemyCount"])
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

            #buff bosses because otherwise unfair
            if networkState.isMultiplayer and networkState.isHost and not prBossScaled:
                prTotalPlayers      = 1 + len(remotePlayers)
                prBossHpMult        = 1 + 0.2 * (prTotalPlayers - 1)
                if prBossHpMult    != 1.0:
                    for e in enemyGroup:
                        if e.enemyName.lower().startswith("boss"):
                            e.hp    = int(e.hp * prBossHpMult)
                            e.maxHp = e.hp
                            if e.ai and hasattr(e.ai, "maxHp"):
                                e.ai.maxHp = e.hp
                            print(f"main: boss HP scaled x{prBossHpMult} -> {e.hp}")
                    prBossScaled = True

        if playerObj.openShop:
            shop.updateShopInstance(layerID=currentLayerID[0])
            playerObj.openShop = False
            result = shop.run(screen, clock, playerObj)
            if result == "quit":
                running = False
            continue

        if currentRoomID == -3 & len(enemyGroup) == 0:
            musicManager.stopBoss()

        if newRoomID != -3 and len(enemyGroup) > 0:
            musicManager.startCombat()
        else:
            musicManager.stopCombat()

        #world state broadcaster
        if networkState.isMultiplayer and networkState.isHost and remotePlayers:
            prEnemies = []
            for e in enemyGroup:
                prPhaseName = ""
                if hasattr(e.ai, "phaseName") and hasattr(e.ai, "desperation"):
                    prPhaseName = e.ai.phaseName
                    if e.ai.desperation:
                        remaining = max(0.0, getattr(e.ai, "desperationTimer", 0.0))
                        prPhaseName = f"{prPhaseName} desperation {remaining:.1f}s"
                prEnemies.append({
                    "id":    id(e),
                    "name":  e.enemyName,
                    "x":     e.rect.x,
                    "y":     e.rect.y,
                    "hp":    e.hp,
                    "maxHp": e.maxHp,
                    "phaseName": prPhaseName,
                })

            prBullets = []
            for b in playerObj.bullets:
                prBullets.append({
                    "x":     b.posX,
                    "y":     b.posY,
                    "w":     b.rect.w,
                    "h":     b.rect.h,
                    "color": list(b.image.get_at((0, 0))[:3]),
                    "owner": 0,
                })
            for cid, rp in remotePlayers.items():
                for b in rp["obj"].bullets:
                    prBullets.append({
                        "x":     b.posX,
                        "y":     b.posY,
                        "w":     b.rect.w,
                        "h":     b.rect.h,
                        "color": list(b.image.get_at((0, 0))[:3]),
                        "owner": cid,
                    })

            for e in enemyGroup:
                if hasattr(e, "ai") and hasattr(e.ai, "bullets"):
                    for b in e.ai.bullets:
                        prBullets.append({
                            "x":     b.posX,
                            "y":     b.posY,
                            "w":     b.rect.w,
                            "h":     b.rect.h,
                            "color": list(b.image.get_at((0, 0))[:3]),
                            "owner": -1,
                        })

            #remaining breakables
            prRemaining = []
            currLayout = roomRegistery[currentRoomID].layout
            for rowIdx, rowData in enumerate(currLayout):
                for colIdx, tileVal in enumerate(rowData):
                    if tileVal == 2:
                        prRemaining.append((rowIdx, colIdx))

            #collect beam data for client rendering
            import math as prMath
            prBeams = []
            for e in enemyGroup:
                if not hasattr(e, "ai") or not hasattr(e.ai, "beamHitsPlayer"):
                    continue
                ai = e.ai
                if hasattr(ai, "beamStart") and hasattr(ai, "beamEnd") and getattr(ai, "beamActive", False):
                    prBeams.append({"x1": ai.beamStart[0], "y1": ai.beamStart[1], "x2": ai.beamEnd[0], "y2": ai.beamEnd[1]})
                if hasattr(ai, "sniperBeam") and ai.sniperBeam is not None:
                    sp, ang = ai.sniperBeam
                    prLen = max(winW, winH) * 2
                    prBeams.append({"x1": sp[0], "y1": sp[1], "x2": sp[0] + prMath.cos(ang) * prLen, "y2": sp[1] + prMath.sin(ang) * prLen})
                if hasattr(ai, "beamLines"):
                    for (sx, sy), (ex, ey) in ai.beamLines:
                        prBeams.append({"x1": sx, "y1": sy, "x2": ex, "y2": ey})
                if hasattr(ai, "beamSpinners"):
                    for spinner in ai.beamSpinners:
                        (ex, ey), (ox, oy) = spinner.getEndpoints()
                        prBeams.append({"x1": ox, "y1": oy, "x2": ex, "y2": ey})
                if hasattr(ai, "lasers"):
                    for laser in ai.lasers:
                        if isinstance(laser, dict) and "pos" in laser and "angle" in laser:
                            lx, ly = laser["pos"]
                            la     = laser["angle"]
                            prLen = max(winW, winH) * 1.5
                            prBeams.append({"x1": lx, "y1": ly, "x2": lx + prMath.cos(la) * prLen, "y2": ly + prMath.sin(la) * prLen})

            prPlayers = [{"id": 0, "x": playerObj.posX, "y": playerObj.posY,
                          "hp": playerObj.hp, "maxHp": playerObj.maxHp,
                          "money": playerObj.money,
                          "inventory": playerObj.inventory,
                          "dead": localPlayerDead}]
            for cid, rp in remotePlayers.items():
                prPlayers.append({"id": cid, "x": rp["obj"].posX, "y": rp["obj"].posY,
                                  "hp": rp["obj"].hp, "maxHp": rp["obj"].maxHp,
                                  "money": rp["obj"].money,
                                  "inventory": rp["obj"].inventory,
                                  "dead": rp["dead"]})

            await networkState.server.broadcast({
                "type":        "worldState",
                "roomId":      currentRoomID,
                "roomPosX":    currentRoomPosX,
                "roomPosY":    currentRoomPosY,
                "doorsLocked": playerObj.doorsLocked,
                "players":     prPlayers,
                "enemies":     prEnemies,
                "bullets":     prBullets,
                "beams":       prBeams,
                "remainingBreakables": prRemaining,
                "gameOver":    gameOver,
                "gameWin":     gameWin,
            })

        pygame.display.flip()

    #network cleanup
    if networkState.isMultiplayer:
        if networkState.server:
            await networkState.server.stop()
        if networkState.client:
            await networkState.client.disconnect()
        networkState.server        = None
        networkState.client        = None
        networkState.isMultiplayer  = False
    remotePlayers.clear()
    localPlayerDead = False
    prShopBusyFor.clear()
    prBossScaled    = False

    pygame.quit()


if __name__ == "__main__":
    asyncio.run(mainAsync())
