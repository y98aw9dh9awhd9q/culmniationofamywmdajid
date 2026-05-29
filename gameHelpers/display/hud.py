import pygame
import const
from mapping.maps import roomRegistery
import mainMenu.theme as theme

heartCache = {}
gunCache   = {}

def loadHeart(path, size):
    key = (path, size)
    if key not in heartCache:
        img = pygame.image.load(path).convert_alpha()
        heartCache[key] = pygame.transform.scale(img, (size, size))
    return heartCache[key]

def loadGun(path, w, h):
    key = (path, w, h)
    if key not in gunCache:
        img = pygame.image.load(path).convert_alpha()
        gunCache[key] = pygame.transform.scale(img, (w, h))
    return gunCache[key]

def drawHearts(screen, playerObj):
    winW, winH = screen.get_size()
    heartSize  = max(20, int(winH * 0.055))
    margin     = max(8, int(winW * 0.012))
    spacing    = max(4, int(heartSize * 0.15))
    fullHeart  = loadHeart(const.fullHeart, heartSize)
    halfHeart  = loadHeart(const.halfHeart, heartSize)
    hp         = max(0, playerObj.hp)
    maxHp      = max(0, playerObj.maxHp)
    slots      = (maxHp + 1) // 2

    for i in range(slots):
        hpValue = hp - i * 2
        if hpValue >= 2:
            img = fullHeart
        elif hpValue == 1:
            img = halfHeart
        else:
            img = fullHeart.copy()
            img.set_alpha(55)
        screen.blit(img, (margin + i * (heartSize + spacing), margin))

    gunY = margin + heartSize + max(4, int(heartSize * 0.2))
    gunH = max(14, int(heartSize * 0.7))
    gunW = gunH * 3

    if hasattr(playerObj, "obtainedGuns") and playerObj.obtainedGuns:
        for gi, gunName in enumerate(playerObj.obtainedGuns):
            try:
                path    = const.gunPths[gunName]
                gunImg  = loadGun(path, gunW, gunH)
                screen.blit(gunImg, (margin + gi * (gunW + spacing), gunY))
            except Exception:
                pass

roomShop   = 1
roomChest  = 5
roomDChest = 6
roomBoss   = -3
roomEntry  = -1
roomExit   = -2
dirMap     = {0: (-1, 0), 1: (1, 0), 2: (0, -1), 3: (0, 1)}
oppDir     = (1, 0, 3, 2)

def adjacentConnected(generatedMap, r, c):
    rows   = len(generatedMap)
    cols   = len(generatedMap[0]) if rows else 0
    if not (0 <= r < rows and 0 <= c < cols):
        return set()
    roomId = generatedMap[r][c]
    if roomId not in roomRegistery:
        return set()
    exits  = roomRegistery[roomId].exits
    result = set()
    for d, (dr, dc) in dirMap.items():
        nr, nc = r + dr, c + dc
        if not (0 <= nr < rows and 0 <= nc < cols):
            continue
        if not exits[d]:
            continue
        nId = generatedMap[nr][nc]
        if nId not in roomRegistery:
            continue
        if roomRegistery[nId].exits[oppDir[d]]:
            result.add((nr, nc))
    return result

def visibleRooms(generatedMap, seen, currentR, currentC):
    rows     = len(generatedMap)
    cols     = len(generatedMap[0]) if rows else 0
    visible  = {(r, c) for r, c in seen if 0 <= r < rows and 0 <= c < cols}
    visible |= adjacentConnected(generatedMap, currentR, currentC)
    visible.add((currentR, currentC))
    return visible

def drawMinimap(screen, generatedMap, currentRoomPosY, currentRoomPosX, roomIdCompendium):
    if not generatedMap:
        return

    winW, winH = screen.get_size()
    cellSize   = max(10, int(winH * 0.032))
    margin     = max(8, int(winW * 0.012))
    gap        = max(2, int(cellSize * 0.12))
    rows       = len(generatedMap)
    cols       = len(generatedMap[0]) if rows else 0
    mapW       = cols * (cellSize + gap) - gap
    mapH       = rows * (cellSize + gap) - gap
    originX    = winW - margin - mapW
    originY    = margin
    seen       = {(r, c) for r, c in roomIdCompendium}
    visible    = visibleRooms(generatedMap, seen, currentRoomPosY, currentRoomPosX)
    panelPad   = max(4, int(cellSize * 0.3))
    panel      = pygame.Surface((mapW + panelPad * 2, mapH + panelPad * 2), pygame.SRCALPHA)
    panel.fill((0, 0, 0, 120))
    screen.blit(panel, (originX - panelPad, originY - panelPad))
    iconFont   = pygame.font.SysFont(const.fontTextBasic, max(10, int(cellSize * 0.9)))

    for r in range(rows):
        for c in range(cols):
            if (r, c) not in visible:
                continue

            x         = originX + c * (cellSize + gap)
            y         = originY + r * (cellSize + gap)
            roomId    = generatedMap[r][c]
            isCurrent = r == currentRoomPosY and c == currentRoomPosX
            hasSeen   = (c, r) in seen

            if isCurrent:
                bgColor = theme.accentDim
            elif hasSeen:
                bgColor = const.green
            else:
                bgColor = (30, 30, 40)

            pygame.draw.rect(screen, bgColor, (x, y, cellSize, cellSize), border_radius=2)

            if roomId in roomRegistery and hasSeen:
                rType  = roomRegistery[roomId].type
                letter = None
                lColor = const.white

                if rType in (roomChest, roomDChest):
                    letter = "C"
                    lColor = theme.textPrimary
                elif rType == roomShop:
                    letter = "S"
                    lColor = theme.textPrimary
                elif roomId == roomBoss or rType == 2:
                    letter = "B"
                    lColor = const.red
                elif roomId == roomExit or rType == 4:
                    letter = "E"
                    lColor = theme.textPrimary

                if letter:
                    surf = iconFont.render(letter, True, lColor)
                    screen.blit(surf, (x + cellSize // 2 - surf.get_width() // 2,
                                       y + cellSize // 2 - surf.get_height() // 2))

            borderColor = theme.borderColor if isCurrent else const.darkgray
            pygame.draw.rect(screen, borderColor, (x, y, cellSize, cellSize), 1, border_radius=2)

def drawGameOver(screen, deathMessage="GAME OVER"):
    winW, winH   = screen.get_size()
    BG           = pygame.image.load(const.loseSceren).convert()
    BG           = pygame.transform.scale(BG, (winW, winH))
    screen.blit(BG, (0, 0))
    fontSize     = max(72, int(winH * 0.14))
    gameOverFont = pygame.font.SysFont(None, fontSize)
    textSurf     = gameOverFont.render(deathMessage, True, const.red)
    screen.blit(textSurf, (winW // 2 - textSurf.get_width() // 2,
                            winH // 2 - textSurf.get_height() // 2))

def drawHud(screen, playerObj, generatedMap, currentRoomPosY, currentRoomPosX, roomIdCompendium):
    drawHearts(screen, playerObj)
    drawMinimap(screen, generatedMap, currentRoomPosY, currentRoomPosX, roomIdCompendium)