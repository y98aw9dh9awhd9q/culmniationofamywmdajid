import pygame
import json
import os
import mainMenu.theme as theme

settingsFile = "data/settings/settings.json"

defaultSettings = {
    "fpsCap"      : 60,
    "displayMode" : "windowed",
    "resolution"  : [900, 600],
    "tutorial"    : True,
    "keybinds"    : {
        "up"      : pygame.K_w,
        "down"    : pygame.K_s,
        "left"    : pygame.K_a,
        "right"   : pygame.K_d,
        "shoot"   : 1,
    },
}

tutorialOptions    = (True, False)
fpsOptions         = (1, 30, 60, 120, 144, 240)
resolutionOptions  = [
    [900,  600],
    [1280, 720],
    [1600, 900],
    [1920, 1080],
]
displayModeOptions = ["windowed", "borderless", "fullscreen"]

def loadSettings():
    if os.path.exists(settingsFile):
        try:
            with open(settingsFile, "r") as f:
                data = json.load(f)
            for k, v in defaultSettings.items():
                data.setdefault(k, v)
            for k, v in defaultSettings["keybinds"].items():
                data["keybinds"].setdefault(k, v)
            return data
        except Exception:
            pass
    return dict(defaultSettings)

def saveSettings(cfg):
    os.makedirs(os.path.dirname(settingsFile), exist_ok=True)
    try:
        with open(settingsFile, "w") as f:
            json.dump(cfg, f, indent=2)
    except Exception:
        pass

def applySettings(cfg):
    w, h = cfg["resolution"]
    mode = cfg["displayMode"]
    if mode == "fullscreen":
        return pygame.display.set_mode((w, h), pygame.FULLSCREEN)
    elif mode == "borderless":
        info = pygame.display.Info()
        return pygame.display.set_mode((info.current_w, info.current_h), pygame.NOFRAME)
    else:
        return pygame.display.set_mode((w, h))

def keyName(val):
    if isinstance(val, int) and val >= 1 and val <= 5:
        names = {1: "LMB", 2: "MMB", 3: "RMB"}
        return names.get(val, f"Mouse{val}")
    try:
        return pygame.key.name(val).upper()
    except Exception:
        return str(val)





generalSection  = "general"
keybindSection = "keybinds"

def run(screen, clock, font):
    cfg = loadSettings()

    titleFont = pygame.font.SysFont(None, 52)
    labelFont = pygame.font.SysFont(None, 34)
    valueFont = pygame.font.SysFont(None, 34)
    hintFont  = pygame.font.SysFont(None, 24)

    rowH   = 60
    startY = 160

    generalRows = [
        ("fps cap"      , "fpsCap"      , "cycle" , fpsOptions         ),
        ("resolution"   , "resolution"  , "cycle" , resolutionOptions  ),
        ("display mode" , "displayMode" , "cycle" , displayModeOptions ),
        ("tutorial"     , "tutorial"    , "cycle" , tutorialOptions    ),
    ]

    #shown keybind actions
    keybindActions = ["up", "down", "left", "right", "shoot"]

    currentSection  = generalSection
    rebindingAction = None    #holds for key press

    def drawArrowButton(surf, rect, direction, hovered):
        pygame.draw.rect(surf, theme.bgHover if hovered else theme.bgMid, rect, border_radius=5)
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
            return list(options).index(val)
        except ValueError:
            return 0

    running = True
    while running:
        winW, winH = screen.get_size()
        colX       = winW // 2
        mx, my     = pygame.mouse.get_pos()
        clock.tick(cfg["fpsCap"])

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                saveSettings(cfg)
                return "quit", screen



            #waits for input
            if rebindingAction is not None:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        rebindingAction = None   # cancel
                    else:
                        cfg["keybinds"][rebindingAction] = event.key
                        rebindingAction = None
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    cfg["keybinds"][rebindingAction] = event.button
                    rebindingAction = None
                continue



            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_BACKSPACE):
                    saveSettings(cfg)
                    screen = applySettings(cfg)
                    return "menu", screen



            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                tabW    = winW // 2
                genRect = pygame.Rect(0,    55, tabW - 2, 36)
                kbRect  = pygame.Rect(tabW, 55, tabW - 2, 36)
                if genRect.collidepoint(mx, my):
                    currentSection = generalSection
                elif kbRect.collidepoint(mx, my):
                    currentSection = keybindSection



                if currentSection == generalSection:
                    for i, (label, key, rowType, options) in enumerate(generalRows):
                        rowY      = startY + i * rowH
                        leftRect  = pygame.Rect(colX + 10,  rowY + 10, 36, 36)
                        rightRect = pygame.Rect(colX + 170, rowY + 10, 36, 36)
                        if rowType == "cycle":
                            idx = currentIndex(key, options)
                            if leftRect.collidepoint(mx, my):
                                cfg[key] = list(options)[(idx - 1) % len(options)]
                            elif rightRect.collidepoint(mx, my):
                                cfg[key] = list(options)[(idx + 1) % len(options)]

                elif currentSection == keybindSection:
                    for i, action in enumerate(keybindActions):
                        rowY       = startY + i * rowH
                        bindRect   = pygame.Rect(colX + 10, rowY + 10, 160, 36)
                        if bindRect.collidepoint(mx, my):
                            rebindingAction = action   # start listening



        screen.fill(theme.bgDark)

        title = titleFont.render("settings", True, theme.textPrimary)
        screen.blit(title, (winW // 2 - title.get_width() // 2, 10))

        #section tabs
        tabW    = winW // 2
        for i, (tabLabel, section) in enumerate([("general", generalSection),
                                                  ("keybinds", keybindSection)]):
            tabRect = pygame.Rect(i * tabW, 55, tabW - 2, 36)
            bgColor = theme.bgHover if currentSection == section else theme.bgMid
            pygame.draw.rect(screen, bgColor, tabRect, border_radius=4)
            pygame.draw.rect(screen, theme.borderColor, tabRect, 1, border_radius=4)
            tColor  = theme.textPrimary if currentSection == section else theme.textSecondary
            lSurf   = labelFont.render(tabLabel, True, tColor)
            screen.blit(lSurf, (tabRect.centerx - lSurf.get_width() // 2,
                                 tabRect.centery - lSurf.get_height() // 2))

        pygame.draw.line(screen, theme.borderColor, (40, 100), (winW - 40, 100), 1)

        if currentSection == generalSection:
            for i, (label, key, rowType, options) in enumerate(generalRows):
                rowY = startY + i * rowH

                labelSurf = labelFont.render(label, True, theme.textSecondary)
                screen.blit(labelSurf, (colX - labelSurf.get_width() - 20, rowY + 14))

                idx       = currentIndex(key, options)
                leftRect  = pygame.Rect(colX + 10,  rowY + 10, 36, 36)
                valueRect = pygame.Rect(colX + 52,  rowY + 10, 112, 36)
                rightRect = pygame.Rect(colX + 170, rowY + 10, 36, 36)

                drawArrowButton(screen, leftRect,  "left",  leftRect.collidepoint(mx, my))
                drawArrowButton(screen, rightRect, "right", rightRect.collidepoint(mx, my))

                pygame.draw.rect(screen, theme.bgMid, valueRect, border_radius=4)
                valSurf = valueFont.render(valueLabel(key, list(options)[idx]), True, theme.textPrimary)
                screen.blit(valSurf, (valueRect.centerx - valSurf.get_width() // 2,
                                      valueRect.centery - valSurf.get_height() // 2))

        elif currentSection == keybindSection:
            for i, action in enumerate(keybindActions):
                rowY      = startY + i * rowH
                isActive  = rebindingAction == action

                labelSurf = labelFont.render(action, True, theme.textSecondary)
                screen.blit(labelSurf, (colX - labelSurf.get_width() - 20, rowY + 14))

                bindRect  = pygame.Rect(colX + 10, rowY + 10, 160, 36)
                bindColor = theme.accent if isActive else theme.bgMid
                pygame.draw.rect(screen, bindColor, bindRect, border_radius=5)
                pygame.draw.rect(screen, theme.borderColor, bindRect, 1, border_radius=5)

                bindText  = "press a key" if isActive else keyName(cfg["keybinds"][action])
                bindSurf  = valueFont.render(bindText, True,
                                             theme.bgDark if isActive else theme.textPrimary)
                screen.blit(bindSurf, (bindRect.centerx - bindSurf.get_width() // 2,
                                       bindRect.centery - bindSurf.get_height() // 2))

        pygame.draw.line(screen, theme.borderColor, (40, winH - 60), (winW - 40, winH - 60), 1)

        hintText = "press key to rebind, esc to cancel" if rebindingAction else "esc to save and go back"
        hint     = hintFont.render(hintText, True, theme.textDim)
        screen.blit(hint, (winW // 2 - hint.get_width() // 2, winH - 40))

        pygame.display.flip()

    return "menu", screen