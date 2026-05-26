import os
import pygame
import mainMenu.theme as theme
import const
from mainMenu.subMenu.settings import loadSettings

normalDescription = ("1x bullets | 1.25x dash i-frames | 1x enemies\n\n\n "
                     "Normal mode for normal people.")

nagraDescription = ("2x bullets | 0.5x dash i-frames | 2x enemies + hp\n\n\n"
                    "Nagra mode, ONLY FOR THE STRONGEST NAGRAS. ")

difficultyDesc = {
    "redacted": "0.1x bullets | infinite dash i-frames | barely any enemies",
    "ign": "0.25x bullets | 2x dash i-frames | 0.25x enemies",
    "easy": "0.5x bullets | 1.5x dash i-frames | 0.5x enemies",
    "normal": normalDescription,
    "hard": "1.25x bullets | 1x dash i-frames | 1.25x enemies",
    "farag": "1.5x bullets | 0.75x dash i-frames | 1.5x enemies + hp",
    "nagra": nagraDescription,
}

def getScaledFont(baseSize, scale):
    return max(12, int(baseSize * scale))

def drawMultilineText(screen, text, font, color, x, y, lineSpacing=1.35):
    for i, line in enumerate(text.split("\n")):
        surf = font.render(line, True, color)
        screen.blit(surf, (x, y + int(font.get_height() * lineSpacing * i)))

def loadDifficultyImage(difficulty, size):
    path = os.path.join(const.baseDir, "assets", "difficulty", f"{difficulty}.png")
    return pygame.transform.smoothscale(pygame.image.load(path).convert_alpha(), size) if os.path.exists(path) else None

def run(screen, clock):
    selected             = const.difficultyOptions.index("normal")
    tutorialEnabled      = False
    running              = True


    while running:
        clock.tick(loadSettings()["fpsCap"])
        winW, winH       = screen.get_size()
        mx, my           = pygame.mouse.get_pos()

        scale            = min(winW / 1600, winH / 900)
        titleFont        = pygame.font.SysFont(const.fontTextBasic, getScaledFont(54, scale))
        sideFont         = pygame.font.SysFont(const.fontTextBasic, getScaledFont(34, scale))
        nameFont         = pygame.font.SysFont(const.fontTextBasic, getScaledFont(48, scale))
        descFont         = pygame.font.SysFont(const.fontTextBasic, getScaledFont(28, scale))
        btnFont          = pygame.font.SysFont(const.fontTextBasic, getScaledFont(36, scale))

        sidebarW         = int(winW * 0.24)
        headerH          = int(90 * scale)
        contentX         = sidebarW + int(30 * scale)
        contentW         = winW - contentX - int(30 * scale)

        pictureRect      = pygame.Rect(contentX, int(160 * scale), min(int(500 * scale), contentW - int(40 * scale)), int(260 * scale))
        startRect        = pygame.Rect(contentX, winH - int(110 * scale), int(220 * scale), int(60 * scale))
        tutorialRect     = pygame.Rect(startRect.right + int(20 * scale), winH - int(110 * scale), int(260 * scale), int(60 * scale))

        buttonY          = int(140 * scale)
        buttonH          = int(52 * scale)
        spacing          = int(12 * scale)
        diffRects        = [pygame.Rect(int(20 * scale), buttonY + i * (buttonH + spacing),
                                        sidebarW - int(40 * scale), buttonH) for i in range(len(const.difficultyOptions))]

        hoveredDiff      = next((i for i, r in enumerate(diffRects) if r.collidepoint(mx, my)), -1)
        hoveringStart    = startRect.collidepoint(mx, my)
        hoveringTutorial = tutorialRect.collidepoint(mx, my)

        for event in pygame.event.get():
            if event.type    == pygame.QUIT:
                return "quit"

            if event.type    == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return None

                if event.key in (pygame.K_UP, pygame.K_w):
                    selected   = (selected - 1) % len(const.difficultyOptions)

                if event.key in (pygame.K_DOWN, pygame.K_s):
                    selected   = (selected + 1) % len(const.difficultyOptions)

                if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    print("difficultySelector:", tutorialEnabled)
                    return (const.difficultyOptions[selected], tutorialEnabled) #no i will not remove it

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if hoveredDiff >= 0:
                    selected = hoveredDiff

                elif hoveringTutorial:
                    tutorialEnabled = not tutorialEnabled

                elif hoveringStart:
                    print("difficultySelecter", tutorialEnabled)
                    return (const.difficultyOptions[selected], tutorialEnabled)

        screen.fill(theme.bgDark)

        screen.blit(titleFont.render("Difficulty", True, theme.textPrimary), (int(30 * scale), int(24 * scale)))

        pygame.draw.line(screen, theme.borderColor, (0, headerH)       , (winW, headerH) , 2)
        pygame.draw.line(screen, theme.borderColor, (sidebarW, headerH), (sidebarW, winH), 2)

        for i, rect in enumerate(diffRects):
            isSelected  = i == selected
            isHovered   = i == hoveredDiff
            bgColor     = theme.bgHover if isSelected else theme.bgMid if isHovered else theme.bgMid
            borderColor = theme.accent if isSelected else theme.borderColor
            txt         = sideFont.render(const.difficultyOptions[i], True,
                                          theme.textPrimary if isSelected else theme.textSecondary)

            pygame.draw.rect(screen, bgColor    , rect,          border_radius=int(10 * scale)) #difficulty button fill
            pygame.draw.rect(screen, borderColor, rect, 2, border_radius=int(8 * scale))  # difficulty button border
            screen.blit(txt, (rect.x + int(14 * scale), rect.centery - txt.get_height() // 2))

        currentDifficulty = const.difficultyOptions[selected]
        screen.blit(nameFont.render(currentDifficulty.upper(), True, theme.textPrimary), (contentX, int(110 * scale)))

        image = loadDifficultyImage(currentDifficulty, (pictureRect.width, pictureRect.height))
        if image:
            screen.blit(image, pictureRect.topleft)
        else:
            pygame.draw.rect(screen, const.red, pictureRect)
            noImgText = descFont.render("NO IMG", True, theme.textPrimary)
            screen.blit(noImgText, (pictureRect.centerx - noImgText.get_width() // 2,
                                    pictureRect.centery - noImgText.get_height() // 2))

        description = difficultyDesc.get(currentDifficulty, "")
        drawMultilineText(screen, description, descFont, theme.textSecondary, contentX, pictureRect.bottom + int(35 * scale))

        #start button
        startBg = theme.accent if hoveringStart else theme.bgHover
        pygame.draw.rect(screen, startBg, startRect, border_radius=int(10 * scale))
        pygame.draw.rect(screen, theme.borderColor, startRect, 2, border_radius=int(10 * scale))
        startText = btnFont.render("Start Game", True, theme.textPrimary)
        screen.blit(startText, (startRect.centerx - startText.get_width() // 2, startRect.centery - startText.get_height() // 2))

        #tutorial button
        tutorialBg = theme.bgHover if hoveringTutorial else theme.bgMid
        pygame.draw.rect(screen, tutorialBg, tutorialRect, border_radius=int(10 * scale))
        pygame.draw.rect(screen, theme.borderColor, tutorialRect, 2, border_radius=int(10 * scale))
        tutorialText = btnFont.render(f"tutorial: {'ON' if tutorialEnabled else 'OFF'}", True, theme.textPrimary)
        screen.blit(tutorialText, (tutorialRect.centerx - tutorialText.get_width() // 2, tutorialRect.centery - tutorialText.get_height() // 2))

        pygame.display.flip()
    return None