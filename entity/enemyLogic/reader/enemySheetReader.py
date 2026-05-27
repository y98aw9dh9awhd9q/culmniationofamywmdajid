import json
import const
import os
import random

def readLayers(layer):
    with open(os.path.join(const.baseDir,"entity/enemyLogic/reader", "enemySheet.json")) as file:
        parsedData = json.load(file)
    result = {}

    for currentLayer in parsedData:
        layerNumber = int(currentLayer)
        if layerNumber <= layer:
            result.update(parsedData[currentLayer])

    return result

def getAvailableEnemies(layer):
    enemies = readLayers(layer)
    return list(enemies.keys())

def getRandomEnemy(layer):
    availableEnemies = getAvailableEnemies(layer)

    if not availableEnemies:
        print("enemySheetReader: no available enemies??????????")
        return None

    return random.choice(availableEnemies)

print(readLayers(1))