import pygame
import mainMenu.theme as theme

creditsText = [
    ("Creation", ["yahu", "keys", "fih"]),
    ("menus", ["keys"])

]

def run(screen, clock):
    titleFont  = pygame.font.SysFont(None, 52)
    headerFont = pygame.font.SysFont(None, 34)
    nameFont   = pygame.font.SysFont(None, 28)
    winW, winH = screen.get_size()

    running = True
    while running:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_BACKSPACE):
                    return "menu"
            if event.type == pygame.MOUSEBUTTONDOWN:
                return "menu"

        screen.fill(theme.bgDark)

        y     = 40
        title = titleFont.render("credits", True, theme.textPrimary)
        screen.blit(title, (winW // 2 - title.get_width() // 2, y))
        y    += 70

        for section, names in creditsText:
            header    = headerFont.render(section, True, theme.accent)
            screen.blit(header, (winW // 2 - header.get_width() // 2, y))
            y        += 36
            for name in names:
                label = nameFont.render(name, True, theme.textSecondary)
                screen.blit(label, (winW // 2 - label.get_width() // 2, y))
                y    += 28
            y        += 14

        hint = nameFont.render("esc to leave", True, theme.textDim)
        screen.blit(hint, (winW // 2 - hint.get_width() // 2, winH - 40))

        pygame.display.flip()

    return "menu"