import pygame
import random
import data.gameSaveData.dataSaving
import mainMenu.subMenu.credits as credits
import mainMenu.subMenu.compendium as compendium
import mainMenu.subMenu.settings as settings
import mainMenu.theme as theme
from mapping.maps import roomRegistery

intervalOfRoomChange = 4.0 #bg room swaps

def getRandomRoomId():
    normalIds = [rid for rid in roomRegistery if rid > 0]
    return random.choice(normalIds)

def run(screen, clock, font):
    titleFont  = pygame.font.SysFont(None, 90)
    buttonFont = pygame.font.SysFont(None, 42)

    #BG cycling
    bgRoomId   = getRandomRoomId()
    bgTimer    = 0.0
    hasSave    = bool(data.gameSaveData.dataSaving.readSave())

    def buildButtons():
        winW, winH = screen.get_size()
        labels     = []
        if hasSave:
            labels.append("continue")
        labels += ["new game", "compendium", "settings", "credits", "exit"]

        #sizes based on window size
        bW          = int(winW * 0.25)
        bH          = int(winH * 0.07)
        bW          = max(220, min(bW, 420))
        bH          = max(45,  min(bH, 80))
        spacing     = int(bH * 0.25)
        totalHeight = len(labels) * bH + (len(labels) - 1) * spacing
        startY      = (winH - totalHeight) // 2

        # -------------------------------------------------------------
        builtButtons = []
        for i, label in enumerate(labels):
            rect = pygame.Rect(winW // 2 - bW // 2, startY + i * (bH + spacing), bW, bH)
            builtButtons.append((label, rect))
        return builtButtons

    buttons = buildButtons()

    running = True
    while running:
        deltaTime = clock.tick(60) / 1000.0
        bgTimer  += deltaTime
        if bgTimer >= intervalOfRoomChange:
            bgRoomId = getRandomRoomId()
            bgTimer  = 0.0

        winW, winH = screen.get_size()
        mx, my     = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit", screen

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for label, rect in buttons:
                    if rect.collidepoint(mx, my):
                        if label == "exit":
                            return "quit", screen

                        if label == "new game":
                            data.gameSaveData.dataSaving.deleteSave()
                            print("menu: new game")
                            return "game", screen

                        if label == "continue":
                            print("menu: continue")
                            return "game", screen

                        if label == "credits":
                            result = credits.run(screen, clock)
                            if result == "quit":
                                return "quit", screen
                            buttons = buildButtons()

                        if label == "compendium":
                            result = compendium.run(screen, clock)
                            if result == "quit":
                                return "quit", screen
                            buttons = buildButtons()

                        if label == "settings":
                            result, screen = settings.run(screen, clock, font)
                            if result == "quit":
                                return "quit", screen
                            buttons = buildButtons()

        screen.fill(theme.bgDark)

        # background room
        try:
            import display
            bgSurf = pygame.Surface((winW, winH))
            display.drawRoom(bgSurf, bgRoomId)
            bgSurf.set_alpha(40)
            screen.blit(bgSurf, (0, 0))
        except Exception:
            pass

        #scales font
        scaledTitleSize = max(40, int(winH * 0.12))
        scaledTitleFont = pygame.font.SysFont(None, scaledTitleSize)
        titleSurf = scaledTitleFont.render("nagra idk", True, theme.textPrimary)
        screen.blit(titleSurf, (winW // 2 - titleSurf.get_width() // 2,
                                 int(winH * 0.10)))

        #buttons
        scaledBtnSize = max(24, int(winH * 0.05))
        scaledBtnFont = pygame.font.SysFont(None, scaledBtnSize)
        for label, rect in buttons:
            hovered   = rect.collidepoint(mx, my)
            bgColor   = theme.bgHover if hovered else theme.bgMid
            pygame.draw.rect(screen, bgColor, rect, border_radius=8)
            pygame.draw.rect(screen, theme.borderColor, rect, 2, border_radius=8)
            textColor = theme.textPrimary if hovered else theme.textSecondary
            text      = scaledBtnFont.render(label, True, textColor)
            screen.blit(text, (rect.centerx - text.get_width() // 2,
                               rect.centery - text.get_height() // 2))

        pygame.display.flip()

    return "quit", screen