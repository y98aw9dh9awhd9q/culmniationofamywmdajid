"""
manages compendium
"""

import os
import const
import data.playerUnlockData.playerData.playerDataManager as playerDataManager
import json

def readJsonCompendium(fileName: str) -> dict:
    try:
        with open(os.path.join(const.baseDir,f"data/playerUnlockData/compendium/compendiumData/{fileName}.json"),"r") as file:
            loadedData = json.load(file)
    except Exception as e:
        print("compendiumManager: compendium error")
        print(f"compendiumManager: {fileName}: {e}")
    return loadedData


"""
tabs = [
    ("enemies", list(readJsonCompendium("enemies").values())),
    ("weapons", list(readJsonCompendium("weapons").values())),
    ("utility", list(readJsonCompendium("utility").values())),
]"""




def updateCompendiumEntries():
    print("compendium manager: called updateCompendiumEntries")
    playerData = playerDataManager.checkCompendiumEntries()
    tabs = []
    for key in playerData:
        tabTemp = []
        for item in playerData[key]:
            #print("t" , readJsonCompendium(key)[item])
            tabTemp.append(readJsonCompendium(key)[item])
        tabs.append((key, tabTemp))
    for item in tabs:
        if "compendium" in item[0] and len(tabs) > 1:
            tabs.remove(item)
    if len(tabs) == 0:
        print(len(tabs))
        tabs = [('compendium', [{'name': 'nothing here', 'image': 'None',
                                 'description': "kill enemies or obtain items to fill in the compendium"}])]
    return tabs

