import mainMenu.menu as menu
from gameHelpers.SHUTDOWN import fullShutdown
def mainMenu(screen,clock,font):
    menuResult, screen = menu.run(screen,clock,font)
    print("menus:", menuResult)
    if menuResult == "quit":
        fullShutdown()
        return None

    return menuResult