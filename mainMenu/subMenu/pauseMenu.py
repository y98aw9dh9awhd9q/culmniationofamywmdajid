import pygame
import mainMenu.theme as theme

def run(screen, clock):
    winW, winH = screen.get_size()

    titleFont  = pygame.font.SysFont(None, 64)
    buttonFont = pygame.font.SysFont(None, 42)

    buttons = [
        ("resume"       , "resume"),
        ("save game"    , "save"),
        ("settings"     , "settings"),
        ("exit to menu" , "menu"),

    ]

    bW          = int(winW * 0.25)
    bH          = int(winH * 0.08)
    bW          = max(220, min(bW, 380))
    bH          = max(48,  min(bH, 80))

    spacing     = int(bH * 0.3)
    totalHeight = len(buttons) * bH + (len(buttons) - 1) * spacing
    startY      = winH // 2 - totalHeight // 2 + 40

    buttonRects = []
    for i, (label, action) in enumerate(buttons):
        rect = pygame.Rect(winW // 2 - bW // 2, startY + i * (bH + spacing), bW, bH)
        buttonRects.append((label, action, rect))

    overlay = pygame.Surface((winW, winH), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 160))

    running = True
    while running:
        mx, my = pygame.mouse.get_pos()
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "resume"

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for label, action, rect in buttonRects:
                    if rect.collidepoint(mx, my):
                        return action

        screen.blit(overlay, (0, 0))

        title = titleFont.render("paused", True, theme.textPrimary)
        screen.blit(title, (winW // 2 - title.get_width() // 2, startY - 80))

        for label, action, rect in buttonRects:
            hovered   = rect.collidepoint(mx, my)
            bgColor   = theme.bgHover if hovered else theme.bgMid
            pygame.draw.rect(screen, bgColor, rect, border_radius=8)
            pygame.draw.rect(screen, theme.borderColor, rect, 2, border_radius=8)
            textColor = theme.textPrimary if hovered else theme.textSecondary
            text      = buttonFont.render(label, True, textColor)
            screen.blit(text, (rect.centerx - text.get_width() // 2,
                               rect.centery - text.get_height() // 2))

        pygame.display.flip()

    return "resume"