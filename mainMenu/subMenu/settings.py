import pygame
import json
import os
import mainMenu.theme as theme

settingsFile = "data/settings/settings.json"

defaultSettings = {
    "fpsCap"      : 60         ,
    "displayMode" : "windowed" ,
    "resolution"  : [900, 600] ,
    "tutorial"    : True       ,
}

tutorialEnabled = (True,False)

fpsOptions        = (1, 30, 60, 120, 144, 240)
resolutionOptions = [
    [67   , 67  ],
    [900  , 600 ],
    [1280 , 720 ],
    [1600 , 900 ],
    [1920 , 1080],
]
displayModeOptions = ["windowed", "borderless", "fullscreen"]

def loadSettings():
    if os.path.exists(settingsFile):
        try:
            with open(settingsFile, "r") as f:
                data = json.load(f)
            for k, v in defaultSettings.items():
                data.setdefault(k, v)
            return data
        except Exception:
            pass
    return dict(defaultSettings)

def saveSettings(cfg):
    try:
        with open(settingsFile, "w") as f:
            json.dump(cfg, f, indent=2)
    except Exception:
        pass

def applySettings(cfg):
    w, h = cfg["resolution"]
    mode = cfg["displayMode"]

    if mode == "fullscreen":
        newScreen = pygame.display.set_mode((w, h), pygame.FULLSCREEN)
    elif mode == "borderless":
        newScreen = pygame.display.set_mode((w, h), pygame.NOFRAME)
    else:
        newScreen = pygame.display.set_mode((w, h))

    return newScreen

def run(screen, clock, font):
    cfg = loadSettings()

    titleFont = pygame.font.SysFont(None, 52)
    labelFont = pygame.font.SysFont(None, 34)
    valueFont = pygame.font.SysFont(None, 34)
    hintFont  = pygame.font.SysFont(None, 24)

    rowH   = 60
    startY = 160

    #rowType "cycle"  -> click left/right arrows to step through options list
    #rowType "toggle" -> click to flip bool
    rows = [
        ("fps cap"      , "fpsCap"      , "cycle"  , fpsOptions         ),
        ("resolution"   , "resolution"  , "cycle"  , resolutionOptions  ),
        ("display mode" , "displayMode" , "cycle"  , displayModeOptions ),
        ("tutorial"     , "tutorial"    , "cycle"  , tutorialEnabled    ),
    ]

    def drawArrowButton(surf, rect, direction, hovered):
        pygame.draw.rect(surf, theme.bgHover if hovered else theme.bgMid,
                         rect, border_radius=5)
        pygame.draw.rect(surf, theme.borderColor, rect, 1, border_radius=5)
        cx, cy = rect.centerx, rect.centery
        pts = ([(cx+8,cy-8),(cx+8,cy+8),(cx-8,cy)] if direction == "left"
               else [(cx-8,cy-8),(cx-8,cy+8),(cx+8,cy)])
        pygame.draw.polygon(surf, theme.accent, pts)

    def valueLabel(key, val):
        if key == "resolution":
            return f"{val[0]}x{val[1]}"
        return str(val)

    def currentIndex(key, options):
        val = cfg[key]
        try:
            return options.index(val)
        except ValueError:
            return 0

    running = True
    while running:
        winW, winH = screen.get_size()
        colX = winW // 2
        mx, my = pygame.mouse.get_pos()
        clock.tick(cfg["fpsCap"])

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                saveSettings(cfg)
                return "quit", screen

            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_BACKSPACE):
                    saveSettings(cfg)
                    screen = applySettings(cfg)
                    return "menu", screen

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for i, (label, key, rowType, options) in enumerate(rows):
                    rowY      = startY + i * rowH
                    leftRect  = pygame.Rect(colX + 10,  rowY + 10, 36, 36)
                    rightRect = pygame.Rect(colX + 170, rowY + 10, 36, 36)

                    if rowType == "cycle":
                        idx = currentIndex(key, options)
                        if leftRect.collidepoint(mx, my):
                            cfg[key] = options[(idx - 1) % len(options)]
                        elif rightRect.collidepoint(mx, my):
                            cfg[key] = options[(idx + 1) % len(options)]

        # draw
        screen.fill(theme.bgDark)

        title = titleFont.render("settings", True, theme.textPrimary)
        screen.blit(title, (winW // 2 - title.get_width() // 2, 60))

        pygame.draw.line(screen, theme.borderColor, (40, 140), (winW - 40, 140), 1)

        for i, (label, key, rowType, options) in enumerate(rows):
            rowY      = startY + i * rowH

            labelSurf = labelFont.render(label, True, theme.textSecondary)
            screen.blit(labelSurf, (colX - labelSurf.get_width() - 20, rowY + 14))

            idx       = currentIndex(key, options)
            leftRect  = pygame.Rect(colX + 10,  rowY + 10, 36, 36)
            valueRect = pygame.Rect(colX + 52,  rowY + 10, 112, 36)
            rightRect = pygame.Rect(colX + 170, rowY + 10, 36, 36)

            drawArrowButton(screen, leftRect,  "left",  leftRect.collidepoint(mx, my))
            drawArrowButton(screen, rightRect, "right", rightRect.collidepoint(mx, my))

            pygame.draw.rect(screen, theme.bgMid, valueRect, border_radius=4)
            valSurf   = valueFont.render(valueLabel(key, options[idx]), True, theme.textPrimary)
            screen.blit(valSurf, (valueRect.centerx - valSurf.get_width() // 2,
                                  valueRect.centery - valSurf.get_height() // 2))

        pygame.draw.line(screen, theme.borderColor, (40, winH - 60), (winW - 40, winH - 60), 1)

        hint = hintFont.render("esc to save and go back", True, theme.textDim)
        screen.blit(hint, (winW // 2 - hint.get_width() // 2, winH - 40))

        pygame.display.flip()

    return "menu", screen