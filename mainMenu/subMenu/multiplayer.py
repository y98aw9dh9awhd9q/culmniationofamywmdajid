import pygame
import mainMenu.theme as theme
from mainMenu.subMenu.settings import loadSettings

def run(screen, clock):
    winW, winH     = screen.get_size()
    titleFont      = pygame.font.SysFont(None, 54)
    btnFont        = pygame.font.SysFont(None, 38)
    inputFont      = pygame.font.SysFont(None, 32)
    hintFont       = pygame.font.SysFont(None, 24)
    defaultPort    = "5555"
    ipInput        = "127.0.0.1"
    portInput      = defaultPort
    activeInput    = None

    buttons        = [
        ("host", "host"),
        ("join", "join"),
        ("back", "back"),
    ]

    bW             = int(winW * 0.28)
    bH             = int(winH * 0.07)
    bW             = max(220, min(bW, 400))
    bH             = max(45,  min(bH, 75))
    spacing        = int(bH * 0.3)
    startY         = int(winH * 0.55)

    buttonRects    = []
    for i, (lbl, act) in enumerate(buttons):
        r = pygame.Rect(winW // 2 - bW // 2, startY + i * (bH + spacing), bW, bH)
        buttonRects.append((lbl, act, r))

    ipRect   = pygame.Rect(winW // 2 - 140, int(winH * 0.38), 280, 40)
    portRect = pygame.Rect(winW // 2 - 140, int(winH * 0.46), 280, 40)

    running = True
    while running:
        cfg          = loadSettings()
        clock.tick(cfg["fpsCap"])
        winW, winH   = screen.get_size()
        mx, my       = pygame.mouse.get_pos()

        hostSelected = False
        joinSelected = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit", None, None

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if activeInput is not None:
                        activeInput = None
                    else:
                        return "back", None, None
                    continue

                if activeInput     == "ip":
                    if event.key   == pygame.K_BACKSPACE:
                        ipInput     = ipInput[:-1]
                    elif event.key == pygame.K_RETURN:
                        activeInput = None
                    else:
                        ipInput    += event.unicode
                elif activeInput   == "port":
                    if event.key   == pygame.K_BACKSPACE:
                        portInput   = portInput[:-1]
                    elif event.key == pygame.K_RETURN:
                        activeInput = None
                    else:
                        if event.unicode.isdigit():
                            portInput += event.unicode

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for lbl, act, rect in buttonRects:
                    if rect.collidepoint(mx, my):
                        if act == "back":
                            return "back", None, None
                        elif act == "host":
                            hostSelected = True
                        elif act == "join":
                            joinSelected = True

                if ipRect.collidepoint(mx, my):
                    activeInput = "ip"
                elif portRect.collidepoint(mx, my):
                    activeInput = "port"
                else:
                    activeInput = None

        if hostSelected:
            try:
                port = int(portInput) if portInput else 5555
            except ValueError:
                port = 5555
            return "host", ipInput, port

        if joinSelected:
            try:
                port = int(portInput) if portInput else 5555
            except ValueError:
                port = 5555
            return "join", ipInput, port

        screen.fill(theme.bgDark)

        title    = titleFont.render("multiplayer", True, theme.textPrimary)
        screen.blit(title, (winW // 2 - title.get_width() // 2, int(winH * 0.06)))

        sepY     = int(winH * 0.15)
        pygame.draw.line(screen, theme.borderColor, (40, sepY), (winW - 40, sepY), 1)

        lblY     = int(winH * 0.20)
        ipLabel  = inputFont.render("your IP address:", True, theme.textSecondary)
        screen.blit(ipLabel, (winW // 2 - ipLabel.get_width() // 2, lblY))

        ipColor  = theme.accent if activeInput == "ip" else theme.bgMid
        pygame.draw.rect(screen, theme.borderColor, ipRect, 2, border_radius=5)
        pygame.draw.rect(screen, ipColor, ipRect.inflate(-4, -4), border_radius=4)
        ipSurf   = inputFont.render(ipInput, True, theme.textPrimary)
        screen.blit(ipSurf, (ipRect.x + 8, ipRect.centery - ipSurf.get_height() // 2))

        portLabel = inputFont.render("port:", True, theme.textSecondary)
        screen.blit(portLabel, (winW // 2 - portLabel.get_width() // 2, ipRect.bottom + 10))

        portColor = theme.accent if activeInput == "port" else theme.bgMid
        pygame.draw.rect(screen, theme.borderColor, portRect, 2, border_radius=5)
        pygame.draw.rect(screen, portColor, portRect.inflate(-4, -4), border_radius=4)
        portSurf  = inputFont.render(portInput, True, theme.textPrimary)
        screen.blit(portSurf, (portRect.x + 8, portRect.centery - portSurf.get_height() // 2))

        for lbl, act, rect in buttonRects:
            hovered = rect.collidepoint(mx, my)
            bg      = theme.bgHover if hovered else theme.bgMid
            pygame.draw.rect(screen, bg, rect, border_radius=8)
            pygame.draw.rect(screen, theme.borderColor, rect, 2, border_radius=8)
            color   = theme.textPrimary if hovered else theme.textSecondary
            text    = btnFont.render(lbl, True, color)
            screen.blit(text, (rect.centerx - text.get_width() // 2, rect.centery - text.get_height() // 2))

        hint = hintFont.render("esc to leave", True, theme.textDim)
        screen.blit(hint, (winW // 2 - hint.get_width() // 2, winH - 40))

        pygame.display.flip()

    return "back", None, None
