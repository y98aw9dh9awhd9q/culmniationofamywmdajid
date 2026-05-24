import pygame

def loadingBar(screen, font, progress, text="poo poo head"):
    screen.fill((10, 10, 10))
    w, h      = screen.get_size()
    barWidth  = int(w * 0.6)
    barHeight = 40
    x         = (w - barWidth) // 2
    y         = (h - barHeight) // 2

    pygame.draw.rect(
        screen,
        (60, 60, 60),
        (x, y, barWidth, barHeight)
    )

    pygame.draw.rect(
        screen,
        (0, 200, 0),
        (
            x,
            y,
            int(barWidth * progress),
            barHeight
        )
    )

    title = font.render(
        text,
        True,
        (255, 255, 255)
    )

    percent = font.render(
        f"{int(progress * 100)}% finished ",
        True,
        (255, 255, 255)
    )

    screen.blit(
        title,
        (x, y - 50)
    )

    screen.blit(percent,(x, y + 50))

    pygame.display.flip()



from gameHelpers.SHUTDOWN import fullShutdown
import asyncio
import json

async def generateEntireWorld(mapGen, screen,font,worldCache):
    if not worldCache:
        worldCache = {}

    totalFloors = 9 * 4
    completed   = 0

    #generates layer 1-9
    for layer in range(1, 10):

        worldCache[str(layer)] = {}

        #geneates floor 1-4
        for floor in range(1, 5):
            if layer == 1 and floor == 1:
                mapGen.size = 3
                mapGen.setupMap(boss=False)
                await mapGen.prGenerateMap()
                worldCache["1"]["1"] = mapGen.result
                completed += 1
                continue

            floorText = f"generating: {layer}-{floor}"
            print(floorText)
            overallProgress = completed / totalFloors
            loadingBar(screen,font,overallProgress,floorText)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    fullShutdown()

            mapGen.size = min(3 + (layer - 1), 9)
            bossFloor = (floor == 4)

            mapGen.setupMap(boss=bossFloor)

            generationTask = asyncio.create_task(mapGen.prGenerateMap())

            #lloading updates===================================
            while not generationTask.done():
                floorProgress = mapGen.progress
                combinedProgress = (completed + floorProgress) / totalFloors

                loadingBar(
                    screen,
                    font,
                    combinedProgress,
                    floorText
                )

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        fullShutdown()

                await asyncio.sleep(0)

            generated = await generationTask
            mapGen.printMap()
            worldCache[str(layer)][str(floor)] = generated
            completed += 1

            saveStructure = {
                "playerData": {
                    "savePrep": None,
                    "weapon": ["pistol#1"],
                    "layer": [1, 1]
                },

                "worldData": {
                    "layers": worldCache
                },

                "metaData": {
                    "visitedRooms": [[0, 0]]
                }
            }

            with open("data/gameSaveData/save.json","w") as file:
                json.dump(
                    saveStructure,
                    file,
                    indent=4
                )

            print(f"saved to save {layer}-{floor}")

    loadingBar(
        screen,
        font,
        1.0,
        "completed generation!"
    )

    await asyncio.sleep(0.5)

    print("mapGeneration: shutting down")

    mapGen.shutdown()

