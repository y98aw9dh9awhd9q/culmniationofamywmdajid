import pygame
import const
from mapping.maps import roomRegistery, tileColors

def spaceCalculator(screen, roomId):
    layout     = roomRegistery[roomId].layout
    rowCount   = len(layout)
    colCount   = len(layout[0])
    winW, winH = screen.get_size()
    blockW     = winW / colCount
    blockH     = winH / rowCount
    return (layout,  #layout     0
            rowCount,#row count  1
            colCount,#col count  2
            blockW,  #blockW     3
            blockH)  #blockH     4


#tile renderer
def drawRoom(screen, roomId):

    layout, rowCount, colCount, blockW, blockH = spaceCalculator(screen, roomId)



    elevator = pygame.transform.scale(pygame.image.load(const.elevator).convert_alpha(), (blockH, blockW))
    chest    = pygame.transform.scale(pygame.image.load(const.chest).convert_alpha()   , (blockH, blockW))
    for rowIdx, rowData in enumerate(layout):
        for colIdx, tileVal in enumerate(rowData):
            tileRect  = pygame.Rect(colIdx * blockW, rowIdx * blockH, blockW, blockH)
            colorName = tileColors.get(tileVal)
            match colorName:
                case "purple" : screen.blit(elevator, tileRect)
                case "yellow" : screen.blit(chest, tileRect)

                case _ if colorName:
                    pygame.draw.rect(
                        screen,
                        getattr(const, colorName),
                        tileRect
                    )

            pygame.draw.rect(screen, const.black, tileRect, 1)



def loadPlayerImage(size):
    try:
        from const import playerDir
        img = pygame.image.load(playerDir)
        return pygame.transform.scale(img, size)
    except Exception:
        #noimage error handing
        surf = pygame.Surface(size)
        surf.fill((0, 200, 255))
        return surf

def loadBulletImg(size = (50,50)):
    try:
        from const import bulletDir
        img = pygame.image.load(bulletDir)
        return pygame.transform.scale(img, size)
    except Exception:
        #noimage error handing
        surf = pygame.Surface(size)
        surf.fill((0, 200, 255))
        return surf

def drawBullet(screen,bulletObj):
    if bulletObj.image is None:
        bulletObj.image = loadBulletImg(bulletObj.size)
    screen.blit(bulletObj.image, bulletObj.rect)


def drawPlayer(screen, playerObj):
    if playerObj.image is None:
        playerObj.image = loadPlayerImage(playerObj.size)
    if not playerObj.isFlickering():
        screen.blit(playerObj.image, playerObj.rect)

#hud
def drawHud(screen, playerObj, roomInfo, font):
    #layer and room label
    if roomInfo:    #very important alignment
        label                          = f"Layer {roomInfo['layerNum']}   Room {roomInfo['layerNum']}-{roomInfo['roomNum']}"
        tag                            = ""
        if roomInfo["isEntrance"]: tag = "  [ENTRANCE]"
        if roomInfo["isBoss"]:     tag = "  [BOSS]"
        roomText = font.render(label + tag, True, const.white)
        screen.blit(roomText, (10, 10))

    #hp
    hpLabel          = font.render("HP", True, const.white)
    screen.blit(hpLabel, (10, 38))
    barX, barY, barH = 40, 40, 14
    maxBarW          = 200
    barW             = int(maxBarW * max(playerObj.hp, 0) / playerObj.maxHp)
    pygame.draw.rect(screen, (80, 0, 0),   pygame.Rect(barX, barY, maxBarW, barH))
    pygame.draw.rect(screen, (220, 40, 40), pygame.Rect(barX, barY, barW,    barH))
    pygame.draw.rect(screen, const.white,  pygame.Rect(barX, barY, maxBarW, barH), 1)

#transition

def drawGameOver(screen, font):
    winW, winH = screen.get_size()
    bigFont    = pygame.font.SysFont(None, 90)
    title      = bigFont.render("skill issue", True, (200, 0, 0))
    sub        = font.render("r to restart esc to quit", True, (180, 180, 180))
    screen.fill(const.black)
    screen.blit(title, title.get_rect(center=(winW // 2, winH // 2 - 30)))
    screen.blit(sub,   sub.get_rect(center=(winW // 2, winH // 2 + 50)))
    pygame.display.flip()