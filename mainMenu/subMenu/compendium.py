import pygame
import const
import mainMenu.theme as theme

# entry guide:
# each entry: {"name": str, "image": path or none, "description": str}
# missing assets show a placeholder
# example asset path "const.basedir/assets/enemies/goon.png"

enemies = [
    {
        "name":        "nagra",
        "image":       None,
        "description": "nagra",
    },
    {
        "name":        "emmanuel",
        "image":       None,
        "description": "gooner",
    },
]

weapons = [
    {
        "name":        "gun",
        "image":       None,
        "description": "g u n",
    },
]

utility = [
    {
        "name":        "healing potion",
        "image":       None,
        "description": "drink",
    },
]

tabs = [
    ("enemies", enemies),
    ("weapons", weapons),
    ("utility", utility),
]

placeholderColor = const.red
imageSize        = (67, 67) #make this unified across enemies based on window scale

def loadImage(path):
    if path is None:
        return None
    try:
        img = pygame.image.load(path).convert_alpha()
        return pygame.transform.scale(img, imageSize)
    except Exception:
        return None

def run(screen, clock):
    titleFont  = pygame.font.SysFont(None, 48)
    tabFont    = pygame.font.SysFont(None, 32)
    nameFont   = pygame.font.SysFont(None, 30)
    descFont   = pygame.font.SysFont(None, 24)
    winW, winH = screen.get_size()

    currentTab = 0
    scrollY    = 0
    entryH     = imageSize[1] + 20    #height per entry row
    listTop    = 100                  #y level where entry list starts
    listBottom = winH - 50
    visibleH   = listBottom - listTop

    #images for tabs
    loadedTabs = []
    for tabName, entries in tabs:
        loaded = []
        for e in entries:
            loaded.append({**e, "surf": loadImage(e["image"])})
        loadedTabs.append((tabName, loaded))

    tabW    = winW // len(tabs)
    running = True

    while running:
        clock.tick(60)
        mx, my = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_BACKSPACE):
                    return "menu"
            if event.type == pygame.MOUSEBUTTONDOWN:
                #check tab clicks
                if my < listTop:
                    for i in range(len(tabs)):
                        if i * tabW <= mx < (i + 1) * tabW:
                            currentTab = i
                            scrollY    = 0
                #goes back if outside
                if my > listBottom:
                    return "menu"
            if event.type == pygame.MOUSEWHEEL:
                scrollY -= event.y * 30
                scrollY  = max(0, scrollY)

        screen.fill(theme.bgDark)

        #title card
        title = titleFont.render("compendium", True, theme.textPrimary)
        screen.blit(title, (winW // 2 - title.get_width() // 2, 10))

        #tab bar
        for i, (tabName, _) in enumerate(loadedTabs):
            tabRect  = pygame.Rect(i * tabW, 55, tabW - 2, 36)
            bgColor  = theme.bgHover if i == currentTab else theme.bgMid
            pygame.draw.rect(screen, bgColor, tabRect, border_radius=4)
            pygame.draw.rect(screen, theme.borderColor, tabRect, 1, border_radius=4)
            labelColor = theme.textPrimary if i == currentTab else theme.textSecondary
            label    = tabFont.render(tabName, True, labelColor)
            screen.blit(label, (tabRect.centerx - label.get_width() // 2,
                                tabRect.centery - label.get_height() // 2))

        clipRect = pygame.Rect(0, listTop, winW, visibleH)
        screen.set_clip(clipRect)

        _, entries = loadedTabs[currentTab]
        for idx, entry in enumerate(entries):
            ey = listTop + idx * entryH - scrollY
            if ey + entryH < listTop or ey > listBottom:
                continue

            rowRect = pygame.Rect(20, ey, winW - 40, entryH - 6)
            pygame.draw.rect(screen, theme.bgMid, rowRect, border_radius=6)
            pygame.draw.rect(screen, theme.borderColor, rowRect, 1, border_radius=6)

            if entry["surf"]:
                screen.blit(entry["surf"], (30, ey + 6))
            else:
                pygame.draw.rect(screen, placeholderColor,
                                 (30, ey + 6, imageSize[0], imageSize[1]),
                                 border_radius=4)
                ph = descFont.render("no img", True, theme.textDim)
                screen.blit(ph, (30 + imageSize[0] // 2 - ph.get_width() // 2,
                                 ey + 6 + imageSize[1] // 2 - ph.get_height() // 2))

            #name & description
            textX = 30 + imageSize[0] + 16
            name  = nameFont.render(entry["name"], True, theme.textPrimary)
            screen.blit(name, (textX, ey + 10))

            #wordwrap
            words = entry["description"].split()
            line  = ""
            lineY = ey + 40
            maxW  = winW - textX - 30
            for word in words:
                test = line + word + " "
                if descFont.size(test)[0] > maxW and line:
                    rendered = descFont.render(line.rstrip(), True, theme.textSecondary)
                    screen.blit(rendered, (textX, lineY))
                    lineY += 22
                    line   = word + " "
                else:
                    line = test
            if line:
                rendered = descFont.render(line.rstrip(), True, theme.textSecondary)
                screen.blit(rendered, (textX, lineY))

        screen.set_clip(None)

        #scroll indicator
        totalH = len(entries) * entryH
        if totalH > visibleH:
            barH = max(30, visibleH * visibleH // totalH)
            barY = listTop + scrollY * (visibleH - barH) // max(1, totalH - visibleH)
            pygame.draw.rect(screen, theme.scrollbarColor,
                             (winW - 8, barY, 6, barH), border_radius=3)

        hint = descFont.render("scroll to browse  esc to escape", True, theme.textDim)
        screen.blit(hint, (winW // 2 - hint.get_width() // 2, winH - 30))

        pygame.display.flip()

    return "menu"