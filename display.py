import pygame
import const
from mapping.maps import rooms, tileColors

#tile renderer
def drawRoom(screen, roomId):
    layout     = rooms[roomId].layout
    rowCount   = len(layout)
    colCount   = len(layout[0])
    winW, winH = screen.get_size()
    blockW     = winW / colCount
    blockH     = winH / rowCount

    for rowIdx, rowData in enumerate(layout):
        for colIdx, tileVal in enumerate(rowData):
            tileRect  = pygame.Rect(colIdx * blockW, rowIdx * blockH, blockW, blockH)
            colorName = tileColors.get(tileVal)
            print(tileRect)
            if colorName == "purple":
                screen.blit(pygame.transform.scale(pygame.image.load(const.chest).convert_alpha(),(blockH,blockW)),tileRect)
            elif colorName:
                pygame.draw.rect(screen, getattr(const, colorName), tileRect)
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

def drawLayerTitle(screen, layerNum, font):
    winW, winH = screen.get_size()
    bigFont    = pygame.font.SysFont(None, 80)
    title      = bigFont.render(f"LAYER  {layerNum}", True, const.white)
    sub        = font.render("press any key to continue", True, (180, 180, 180))
    screen.fill(const.black)
    screen.blit(title, title.get_rect(center=(winW // 2, winH // 2 - 30)))
    screen.blit(sub,   sub.get_rect(center=(winW // 2, winH // 2 + 40)))
    pygame.display.flip()

def drawBossWarning(screen, layerNum, font):
    winW, winH = screen.get_size()
    bigFont    = pygame.font.SysFont(None, 72)
    title      = bigFont.render(f"boss  {layerNum}-4", True, (220, 40, 40))
    sub        = font.render("press any key to enter", True, (180, 180, 180))
    screen.fill(const.black)
    screen.blit(title, title.get_rect(center=(winW // 2, winH // 2 - 30)))
    screen.blit(sub,   sub.get_rect(center=(winW // 2, winH // 2 + 40)))
    pygame.display.flip()

def drawGameOver(screen, font):
    winW, winH = screen.get_size()
    bigFont    = pygame.font.SysFont(None, 90)
    title      = bigFont.render("skill issue", True, (200, 0, 0))
    sub        = font.render("r to restart esc to quit", True, (180, 180, 180))
    screen.fill(const.black)
    screen.blit(title, title.get_rect(center=(winW // 2, winH // 2 - 30)))
    screen.blit(sub,   sub.get_rect(center=(winW // 2, winH // 2 + 50)))
    pygame.display.flip()

def drawEnding(screen, font):
    winW, winH = screen.get_size()
    bigFont    = pygame.font.SysFont(None, 72)
    subFont    = pygame.font.SysFont(None, 36)
    title      = bigFont.render("you escaped epstein island", True, (255, 220, 60))
    line1      = subFont.render("all 9 layers of epstein", True, (200, 200, 200))
    line2      = subFont.render("you will not get diddled", True, (200, 200, 200))
    restart    = font.render("r to restart esc to quit", True, (140, 140, 140))
    screen.fill(const.black)
    screen.blit(title,   title.get_rect(center=(winW // 2, winH // 2 - 70)))
    screen.blit(line1,   line1.get_rect(center=(winW // 2, winH // 2)))
    screen.blit(line2,   line2.get_rect(center=(winW // 2, winH // 2 + 36)))
    screen.blit(restart, restart.get_rect(center=(winW // 2, winH // 2 + 90)))
    pygame.display.flip()