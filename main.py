import pygame
import const
import mapping.mapGenerator as mapGenerator
import display
from player import player

playingState    = "playing"
layerCardState = "layerCard"
bossWarningState  = "bossWarn"
gameOverState  = "gameOver"
endState     = "ending"
flashDuration   = 0.25

def buildGame():
    sequence   = mapGenerator.buildSequence()
    roomIndex  = 0
    return sequence, roomIndex


def main():
    pygame.init()
    screen              = pygame.display.set_mode((900, 600))
    pygame.display.set_caption("Dungeon")
    clock               = pygame.time.Clock()
    font                = pygame.font.SysFont(None, 28)
    winW, winH          = screen.get_size()
    sequence, roomIndex = buildGame()
    p                   = player(winW, winH)
    gameState           = layerCardState
    flashTimer          = 0.0
    pendingRoomIndex    = None

    def currentInfo():
        return mapGenerator.getRoomInfo(sequence, roomIndex)

    def loadRoom(idx):
        nonlocal roomIndex
        roomIndex = idx
        p.respawn(winW, winH)

    #main loop
    running = True
    while running:
        deltaTime = clock.tick(60) / 1000.0
        events    = pygame.event.get()

        for event in events:
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

                #overlay
                if gameState == layerCardState:
                    gameState = playingState

                elif gameState == bossWarningState:
                    gameState = playingState

                elif gameState in (gameOverState, endState):
                    if event.key == pygame.K_r:
                        sequence, roomIndex = buildGame()
                        p                   = player(winW, winH)
                        gameState           = layerCardState
                        flashTimer          = 0.0
                        pendingRoomIndex    = None

        #splash state render
        if gameState == layerCardState:
            info = currentInfo()
            display.drawLayerTitle(screen, info["layerNum"] if info else 1, font)
            continue

        if gameState == bossWarningState:
            info = currentInfo()
            display.drawBossWarning(screen, info["layerNum"] if info else 1, font)
            continue

        if gameState == gameOverState:
            display.drawGameOver(screen, font)
            continue

        if gameState == endState:
            display.drawEnding(screen, font)
            continue

        #playing state
        info          = currentInfo()
        currentRoomId = info["roomId"] if info else "entrance"

        #draw bg and room
        screen.fill(const.black)
        display.drawRoom(screen, currentRoomId)

        #update player logic
        touchedExit = p.update(deltaTime, currentRoomId)
        display.drawPlayer(screen, p)

        #transition
        if flashTimer > 0:
            flashTimer -= deltaTime
            if flashTimer <= 0 and pendingRoomIndex is not None:
                loadRoom(pendingRoomIndex)
                pendingRoomIndex = None
                info             = currentInfo()
                if info and info["isEntrance"] and info["layerNum"] > 1:
                    gameState = layerCardState
                elif info and info["isBoss"]:
                    gameState = bossWarningState

        #exit
        elif touchedExit and pendingRoomIndex is None:
            nextIndex = roomIndex + 1
            nextInfo  = mapGenerator.getRoomInfo(sequence, nextIndex)

            if nextInfo is None:
                gameState = endState
            else:
                pendingRoomIndex = nextIndex
                flashTimer       = flashDuration

        #death
        if not p.isAlive:
            gameState = gameOverState

        #hud
        display.drawHud(screen, p, info, font)
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()