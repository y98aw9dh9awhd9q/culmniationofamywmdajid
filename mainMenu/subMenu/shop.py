import pygame
from pygame import Surface

import const
import mainMenu.theme as theme

from mainMenu.subMenu.settings import loadSettings


imageSize = (67, 67)


def loadImage(path: str) -> Surface | None: #"type safety -keys i think"
    if path is None:
        return None

    try:
        img = pygame.image.load(path).convert_alpha()
        return pygame.transform.scale(img, imageSize)
    except Exception as e:
        print(f"shop: failed loading image {e}")
        return None


shopItems ={
    0:[
    {
        "id": "HP1",
        "name": "healing potion",
        "description": "heals you :) the heal will in crease with time. You get a tutorial discount!",
        "price": 5,
        "stock": 3,
        "maxStock": 3,
        "image": const.healingPot
    }],

    1: [
    {
        "id": "HP1",
        "name": "healing potion",
        "description": "heals you :) the heal will in crease with time",
        "price": 15,
        "stock": 3,
        "maxStock": 3,
        "image": const.healingPot
    }

    ],
    2: [
    {
        "id": "HP1",
        "name": "healing potion",
        "description": "heals you :) the heal will in crease with time",
        "price": 15,
        "stock": 4,
        "maxStock": 4,
        "image": const.healingPot
    },
        {
            "id": "shotgun",
            "name": "shotgun",
            "description": "heals you :) the heal will in crease with time",
            "price": 50,
            "stock": 1,
            "maxStock": 1,
            "image": const.gunPths["basicShotgun"]
        },
        {
            "id": "assaultRifle",
            "name": "assault rifle",
            "description": "shoots bullets with low cooldown",
            "price": 5,
            "stock": 1,
            "maxStock": 1,
            "image": const.gunPths["assaultRifle"]
        }
    ]




}





class shop:
    def __init__(self):
        global shotItems
        self.layerID = 0
        self.items = shopItems[self.layerID]
        for item in self.items:
            item["surf"] = loadImage(item["image"])

    def resetStock(self):
        for item in self.items:
            item["stock"] = item["maxStock"]

    def giveItem(self, player, item):
        match item["id"]:
            case "HP1": player.getItem("HP1")
            case "shotgun": player.getWeapon("shotgun")
            case "assaultRifle": player.getWeapon("assaultRifle")

    def buy(self, player, itemIndex):
        item = self.items[itemIndex]

        if item["stock"] <= 0:
            return False, "out of stock"

        if player.money < item["price"]:
            return False, "not enough money"

        player.money -= item["price"]
        item["stock"] -= 1

        self.giveItem(player, item)

        return True, "purchased"

    def updateStuff(self):
        self.items = shopItems[self.layerID]



shopInstance = shop()
def updateShopInstance(layerID):
    global shopInstance
    shopInstance.layerID = layerID
    shopInstance.updateStuff()


def run(screen, clock, player):
    titleFont  = pygame.font.SysFont(None, 48)
    nameFont   = pygame.font.SysFont(None, 30)
    descFont   = pygame.font.SysFont(None, 24)
    winW, winH = screen.get_size()
    scrollY    = 0

    try:
        shopKeeperSurf = pygame.image.load(const.shopKeeper).convert_alpha()
        keeperSize     = (int(winW * 0.35),int(winH * 0.30))
        shopKeeperSurf = pygame.transform.scale(shopKeeperSurf,keeperSize)

    except Exception as e:
        print("shop:", e)
        shopKeeperSurf = None

    loadedItems = []

    for item in shopInstance.items:
        loadedItems.append({**item,"surf": loadImage(item["image"])})

    entryH              = 90
    keeperSectionTop    = 60
    keeperSectionHeight = int(winH * 0.35)
    listTop             = keeperSectionTop + keeperSectionHeight + 10
    listBottom          = winH - 50
    visibleH            = listBottom - listTop
    running             = True

    while running:
        clock.tick(loadSettings()["fpsCap"])
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE,pygame.K_BACKSPACE):
                    return "menu"

            if event.type  == pygame.MOUSEWHEEL:
                scrollY    -= event.y * 30
                scrollY     = max(0, scrollY)

            if event.type  == pygame.MOUSEBUTTONDOWN:
                mx, my      = pygame.mouse.get_pos()
                for i, item in enumerate(loadedItems):
                    rowY    = listTop + i * entryH - scrollY
                    buyRect = pygame.Rect(winW - 130, rowY + 20, 90, 40)

                    if buyRect.collidepoint(mx, my):
                        shopInstance.buy(player, i)

        screen.fill(theme.bgDark)

        title = titleFont.render(
            "the amazing digital shop",
            False, theme.textPrimary
        )

        screen.blit(title, (winW // 2 - title.get_width() // 2,  10))
        moneyText = nameFont.render( f"${player.money}", True, theme.textPrimary)
        screen.blit(moneyText, (20, 20))

        jaxRect = pygame.Rect(20, keeperSectionTop, winW - 40, keeperSectionHeight)

        pygame.draw.rect(screen, theme.bgMid, jaxRect, border_radius=8)

        pygame.draw.rect(screen, theme.borderColor, jaxRect, 2, border_radius=8)

        if shopKeeperSurf:
            imageX = (jaxRect.centerx - shopKeeperSurf.get_width() // 2)
            imageY = (jaxRect.centery - shopKeeperSurf.get_height()// 2)

            screen.blit(shopKeeperSurf, (imageX, imageY))

        keeperText = nameFont.render(
            "IF YOU LIKE SEEING ME LIKE THIS YOU'RE THE PROBLEM",
            True,theme.textPrimary)

        screen.blit(keeperText,(jaxRect.centerx - keeperText.get_width() // 2, jaxRect.bottom - 35))

        clipRect = pygame.Rect(0, listTop, winW, visibleH)
        screen.set_clip(clipRect)
        for idx, item in enumerate(loadedItems):
            ey = listTop + idx * entryH - scrollY
            if ey + entryH < listTop:
                continue

            if ey > listBottom:
                continue

            rowRect = pygame.Rect(20, ey, winW - 40, entryH - 6)
            pygame.draw.rect(screen, theme.bgMid, rowRect, border_radius=6)

            pygame.draw.rect(screen, theme.borderColor, rowRect, 1, border_radius=6)

            if item["surf"]:
                screen.blit(item["surf"], (30, ey + 10))

            textX = 120

            nameText = nameFont.render(item["name"], True, theme.textPrimary)

            screen.blit(nameText, (textX, ey + 8))

            descText = descFont.render(item["description"], True, theme.textSecondary)

            screen.blit(descText, (textX, ey + 35))

            stockText = descFont.render(
                f"stock: {item['stock']}",
                True, theme.textSecondary)

            screen.blit(stockText, (textX + 260, ey + 8))

            priceText = descFont.render(f"${item['price']}", True, theme.textPrimary)

            screen.blit(priceText, (textX + 260, ey + 35))

            buyRect = pygame.Rect(winW - 130, ey + 20, 90, 40)

            canBuy = (item["stock"] > 0 and player.money >= item["price"])

            pygame.draw.rect(screen, theme.bgHover if canBuy else theme.bgDark, buyRect, border_radius=5)

            buyText = descFont.render("purchase", True, theme.textPrimary)

            screen.blit(
                buyText,
                (buyRect.centerx - buyText.get_width() // 2, buyRect.centery - buyText.get_height() // 2)
            )

        screen.set_clip(None)
        pygame.display.flip()

    return "menu"