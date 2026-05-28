import pygame
import const
from mapping.maps import roomRegistery
import mainMenu.theme as theme

heartCache = {}

def loadHeart(path, size):
    key = (path, size)
    if key not in heartCache:
        img = pygame.image.load(path).convert_alpha()
        heartCache[key] = pygame.transform.scale(img, (size, size))

    return heartCache[key]

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

        x = margin + i * (heartSize + spacing)
        y = margin

        screen.blit(img, (x, y))

roomShop = 1
roomChest = 5
roomDChest = 6
roomBoss = -3
roomEntry = -1
roomExit = -2

directions = ((-1, 0), (1, 0), (0, -1), (0, 1))

def connectedRooms(generatedMap, startR, startC):
    rows    = len(generatedMap)
    cols    = len(generatedMap[0]) if rows else 0
    visited = set()
    queue   = [(startR, startC)]

    visited.add((startR, startC))

    while queue:
        r, c   = queue.pop(0)
        roomId = generatedMap[r][c]

        if roomId not in roomRegistery:
            continue

        exits = roomRegistery[roomId].exits

        dirMap = {
            0: (-1, 0),
            1: (1, 0),
            2: (0, -1),
            3: (0, 1)
        }

        for d, (dr, dc) in dirMap.items():
            nr = r + dr
            nc = c + dc

            if (nr, nc) in visited:
                continue

            if not (0 <= nr < rows and 0 <= nc < cols):
                continue

            if not exits[d]:
                continue

            nId = generatedMap[nr][nc]

            if nId not in roomRegistery:
                continue

            opp = (1, 0, 3, 2)[d]

            if roomRegistery[nId].exits[opp]:
                visited.add((nr, nc))
                queue.append((nr, nc))

    return visited

def drawMinimap(screen,generatedMap,currentRoomPosY,currentRoomPosX,roomIdCompendium):
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
    visited    = connectedRooms(generatedMap,currentRoomPosY,currentRoomPosX)
    seen       = {(r, c) for r, c in roomIdCompendium}
    panelPad   = max(4, int(cellSize * 0.3))
    panel      = pygame.Surface((mapW + panelPad * 2, mapH + panelPad * 2),pygame.SRCALPHA)

    panel.fill((0, 0, 0, 120))
    screen.blit(panel, (originX - panelPad, originY - panelPad))

    iconFont = pygame.font.SysFont(const.fontTextBasic,max(10, int(cellSize * 0.9)))

    for r in range(rows):
        for c in range(cols):

            if (r, c) not in visited:
                continue

            x = originX + c * (cellSize + gap)
            y = originY + r * (cellSize + gap)

            roomId = generatedMap[r][c]

            isCurrent = r == currentRoomPosY and c == currentRoomPosX

            hasSeen = (r, c) in seen

            if isCurrent:
                bgColor = theme.accentDim

            elif not hasSeen:
                bgColor = theme.borderColor

            else:
                bgColor = theme.textSecondary

            pygame.draw.rect(
                screen,
                bgColor,
                (x, y, cellSize, cellSize),
                border_radius=2
            )

            #letter overlay for special rooms
            if roomId in roomRegistery and hasSeen:

                rType = roomRegistery[roomId].type

                letter = None
                lColor = const.white

                if rType in (roomChest, roomDChest):
                    letter = "C"
                    lColor = theme.textPrimary

                elif rType == roomShop:
                    letter = "S"
                    lColor = theme.textPrimary

                elif rType == roomBoss:
                    letter = "B"
                    lColor = const.red

                elif rType == roomExit:
                    letter = "E"
                    lColor = theme.textPrimary

                if letter:
                    surf = iconFont.render(letter, True, lColor)

                    screen.blit(surf,(x + cellSize // 2 - surf.get_width() // 2,y + cellSize // 2 - surf.get_height() // 2))

            borderColor = theme.borderColor if isCurrent else const.darkgray

            pygame.draw.rect(screen,borderColor,(x, y, cellSize, cellSize),1,border_radius=2)

def drawGameOver(screen,deathMessage="GAME OVER"):
    winW, winH   = screen.get_size()
    BG           = pygame.image.load(const.loseSceren).convert()
    BG           = pygame.transform.scale(BG, (winW, winH))
    screen.blit(BG, (0,0))
    fontSize     = max(72, int(winH * 0.14))
    gameOverFont = pygame.font.SysFont(None,fontSize)
    textSurf = gameOverFont.render(deathMessage,True,const.red)
    textX = (winW // 2) - (textSurf.get_width() // 2)
    textY = (winH // 2) - (textSurf.get_height() // 2)
    screen.blit(textSurf,(textX, textY))

def drawHud(screen,playerObj,generatedMap,currentRoomPosY,currentRoomPosX,roomIdCompendium):
    drawHearts(screen, playerObj)
    drawMinimap(screen,generatedMap,currentRoomPosY,currentRoomPosX,roomIdCompendium)