import mainMenu.menu as menu
import gameHelpers.networkState as networkState

from mainMenu.subMenu.pregameLobby import runLobby
from gameHelpers.SHUTDOWN          import fullShutdown


async def mainMenu(screen, clock, font):
    while True:
        menuResult, screen = menu.run(screen, clock, font)
        print("menus:", menuResult)
        if menuResult == "quit":
            fullShutdown()
            return None

        if isinstance(menuResult, tuple) and len(menuResult) == 2:
            return menuResult

        if isinstance(menuResult, tuple) and len(menuResult) > 2 and menuResult[0] == "multiplayer":
            _, mode, ip, port     = menuResult
            isHost                = mode == "host"
            networkState.isMultiplayer = True
            networkState.isHost   = isHost
            networkState.hostIp   = ip
            networkState.port     = port
            lobbyResult           = await runLobby(screen, clock, isHost=isHost, hostIp=ip, port=port)
            if lobbyResult == "quit":
                networkState.isMultiplayer = False
                networkState.isHost   = False
                networkState.server    = None
                networkState.client    = None
                continue
            return (networkState.multiplayerDifficulty, False)

        return menuResult
