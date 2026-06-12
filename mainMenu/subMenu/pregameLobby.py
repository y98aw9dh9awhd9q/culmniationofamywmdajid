import asyncio
import pygame
import const
import mainMenu.theme as theme
import gameHelpers.network as network
import gameHelpers.networkState as networkState
from mainMenu.subMenu.settings import loadSettings


async def runLobby(screen, clock, isHost=False, hostIp="127.0.0.1", port=5555):
    titleFont    = pygame.font.SysFont(None, 48)
    infoFont     = pygame.font.SysFont(None, 30)
    playerFont   = pygame.font.SysFont(None, 36)
    btnFont      = pygame.font.SysFont(None, 38)
    hintFont     = pygame.font.SysFont(None, 24)
    diffFont     = pygame.font.SysFont(None, 32)
    server       = None
    client       = None
    playerList   = []
    startRect    = None
    diffOptions  = const.difficultyOptions
    diffIdx      = diffOptions.index(networkState.multiplayerDifficulty) if networkState.multiplayerDifficulty in diffOptions else 0
    diffRect     = None

    if isHost:
        server                    = network.gameServer(port=port)
        networkState.server       = server
        try:
            actualIp, actualPort  = await server.start()
            asyncio.create_task(server.prBroadcastPlayerList())
            statusText            = f"hosting on {actualIp}:{actualPort}"
        except Exception as e:
            statusText            = f"failed to host: {e}"
            server                = None
            networkState.server   = None
    else:
        client                    = network.gameClient(host=hostIp, port=port, name="Player")
        networkState.client       = client
        ok                        = await client.connect()
        if ok:
            statusText            = f"connected to {hostIp}:{port}"
        else:
            statusText            = f"failed to connect to {hostIp}:{port}"
            client                = None
            networkState.client   = None

    running = True
    result  = "lobby"

    while running:
        cfg = loadSettings()
        clock.tick(cfg["fpsCap"])
        winW, winH = screen.get_size()
        mx, my     = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                result    = "quit"
                running   = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                result    = "quit"
                running   = False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if isHost and startRect and startRect.collidepoint(mx, my):
                    diff = diffOptions[diffIdx]
                    networkState.multiplayerDifficulty = diff
                    await server.broadcast({"type": "start", "difficulty": diff})
                    result  = "start"
                    running = False
                if isHost and diffRect and diffRect.collidepoint(mx, my):
                    diffIdx = (diffIdx + 1) % len(diffOptions)
                    networkState.multiplayerDifficulty = diffOptions[diffIdx]

        if isHost and server:
            msgs = await server.getMessages()
            for msg in msgs:
                if msg.get("type") == "join":
                    await server.prBroadcastPlayerList()

            playerList = [
                {"id": 0, "name": "host"}
            ] + [
                {"id": cid, "name": info["name"]}
                for cid, info in server.clients.items()
            ]

        if not isHost and client:
            msgs = await client.getMessages()
            for msg in msgs:
                if msg.get("type") == "playerList":
                    playerList = msg.get("players", [])
                if msg.get("type") == "start":
                    diff = msg.get("difficulty", "normal")
                    networkState.multiplayerDifficulty = diff
                    print(f"[LOBBY] Host started the game! difficulty={diff}")
                    result  = "start"
                    running = False

        if not running:
            break

        screen.fill(theme.bgDark)

        if isHost:
            title = titleFont.render("pregame lobby (HOST)", True, theme.textPrimary)
        else:
            title = titleFont.render("pregame lobby (CLIENT)", True, theme.textPrimary)
        screen.blit(title, (winW // 2 - title.get_width() // 2, int(winH * 0.06)))

        sep = int(winH * 0.15)
        pygame.draw.line(screen, theme.borderColor, (40, sep), (winW - 40, sep), 1)

        statusSurf = infoFont.render(statusText, True, theme.textSecondary)
        screen.blit(statusSurf, (winW // 2 - statusSurf.get_width() // 2, int(winH * 0.18)))

        if (isHost and server is None) or (not isHost and client is None):
            errColor = theme.danger if hasattr(theme, "danger") else (220, 60, 60)
            errSurf  = hintFont.render("ESC to return", True, errColor)
            screen.blit(errSurf, (winW // 2 - errSurf.get_width() // 2, int(winH * 0.28)))
        else:
            playersHeader = infoFont.render("connected players:", True, theme.textDim)
            screen.blit(playersHeader, (int(winW * 0.15), int(winH * 0.26)))

            if playerList:
                for i, p in enumerate(playerList):
                    pname = p.get("name", f"player {p.get('id', '?')}")
                    color = theme.accent if p.get("id") == 0 else theme.textSecondary
                    psurf = playerFont.render(f"{pname}", True, color)
                    screen.blit(psurf, (int(winW * 0.15), int(winH * 0.32) + i * 36))
            else:
                psurf = playerFont.render("(none)", True, theme.textDim)
                screen.blit(psurf, (int(winW * 0.15), int(winH * 0.32)))

            if isHost and server:
                #difficulty selector
                diffLabel = f"Difficulty: {diffOptions[diffIdx]}"
                dSurf     = diffFont.render(diffLabel, True, theme.textPrimary)
                dRect     = dSurf.get_rect(center=(winW // 2, int(winH * 0.55)))


                diffRect  = dRect.inflate(40, 10)
                dhover    = diffRect.collidepoint(mx, my)
                dColor    = theme.accent if dhover else theme.textDim
                dSurf     = diffFont.render(diffLabel, True, dColor)
                screen.blit(dSurf, dRect)
                dHint     = hintFont.render("(click to change)", True, theme.textDim)
                screen.blit(dHint, (winW // 2 - dHint.get_width() // 2, int(winH * 0.60)))


                bW           = int(winW * 0.25)
                bH           = int(winH * 0.07)
                bW           = max(200, min(bW, 350))
                bH           = max(45,  min(bH, 70))
                startRect    = pygame.Rect(winW // 2 - bW // 2, int(winH * 0.70), bW, bH)
                hovering     = startRect.collidepoint(mx, my)

                bg = theme.accent if hovering else theme.bgHover
                pygame.draw.rect(screen, bg, startRect, border_radius=8)
                pygame.draw.rect(screen, theme.borderColor, startRect, 2, border_radius=8)
                stext = btnFont.render("start game", True, theme.textPrimary)
                screen.blit(stext, (startRect.centerx - stext.get_width() // 2, startRect.centery - stext.get_height() // 2))

            if not isHost:
                waitText = hintFont.render("waiting for host", True, theme.textDim)
                screen.blit(waitText, (winW // 2 - waitText.get_width() // 2, int(winH * 0.72)))

        hintText = "esc to quit lobby"
        hint     = hintFont.render(hintText, True, theme.textDim)
        screen.blit(hint, (winW // 2 - hint.get_width() // 2, winH - 40))

        pygame.display.flip()
        await asyncio.sleep(0)

    if result == "quit":
        if server:
            await server.stop()
        if client:
            await client.disconnect()
        networkState.server = None
        networkState.client = None

    return result
