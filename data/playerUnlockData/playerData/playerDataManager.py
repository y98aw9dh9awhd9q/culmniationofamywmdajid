"""
manages permanant player data
"""

import os
import const
import json

playerDataPth = os.path.join(const.baseDir,f"data/playerUnlockData/playerData/playerData.json")

defaultDataToDump = {
    "unlockedCompendiumEntries" : {
        "weapons" : [],
        "utility" : [],
        "enemies" : [],
        "books"   : []
    },
}


#ensure player data exists
if not os.path.exists(playerDataPth):
    with open(playerDataPth,"w") as file:
        json.dump(defaultDataToDump,file)



def writeJson(data: dict) -> None:
    with open(playerDataPth, "w") as file:
        json.dump(data, file)

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
        #print(key, value)
        if len(readData[key]) != 0 and readData[key] is not None:
            dataDict.update({key:value})
    return dataDict





