"""
manages permanant player data
"""

import os
import const
import json

playerDataPth = os.path.join(const.baseDir,f"data/playerUnlockData/playerData/playerData.json")

enemyKillRequirements = {
    "fodder" : 1
}

defaultDataToDump = {
    "unlockedCompendiumEntries" : {
        "weapons"     : [],
        "utility"     : [],
        "enemies"     : [],
        "books"       : [],
        "achievements": []
    },

    "enemyKills" : {}
}


#ensure player data exists
if not os.path.exists(playerDataPth):
    with open(playerDataPth,"w") as file:
        json.dump(defaultDataToDump,file)



def writeCompendiumEntry(key,value) -> None:
    data = readJsonPlayerDat()

    if value not in data["unlockedCompendiumEntries"][key]:
        data["unlockedCompendiumEntries"][key].append(value)

    with open(playerDataPth, "w") as file:
        json.dump(data, file)

def addEnemyKill(enemyName) -> None:
    data = readJsonPlayerDat()

    if enemyName not in data["enemyKills"]:
        data["enemyKills"][enemyName] = 0

    data["enemyKills"][enemyName] += 1

    if enemyName in enemyKillRequirements:
        requiredKills = enemyKillRequirements[enemyName]

        if data["enemyKills"][enemyName] >= requiredKills:
            if enemyName not in data["unlockedCompendiumEntries"]["enemies"]:
                data["unlockedCompendiumEntries"]["enemies"].append(enemyName)

    with open(playerDataPth, "w") as file:
        json.dump(data, file)

def getEnemyKills(enemyName) -> int:
    data = readJsonPlayerDat()

    if enemyName not in data["enemyKills"]:
        return 0

    return data["enemyKills"][enemyName]

def readJsonPlayerDat() -> dict:
    try:
        with open(playerDataPth,"r") as file:
            loadedData = json.load(file)
    except Exception as e:
        print("playerDataManager: data error")
        print(f"playerDataManager: {playerDataPth}: {e}")
    return loadedData

def checkCompendiumEntries():
    readData = readJsonPlayerDat()["unlockedCompendiumEntries"]
    dataDict = {}

    for key, value in readData.items():
        if len(readData[key]) != 0 and readData[key] is not None:
            dataDict.update({key:value})

    print("datadict ", dataDict)
    return dataDict