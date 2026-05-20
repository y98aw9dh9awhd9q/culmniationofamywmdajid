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

tabs = [
    ("enemies", list(readJsonCompendium("enemies").values())),
    ("weapons", list(readJsonCompendium("weapons").values())),
    ("utility", list(readJsonCompendium("utility").values())),
]