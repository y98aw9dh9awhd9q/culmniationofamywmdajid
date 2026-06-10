import json
import os

savePath = "data/gameSaveData/save.json"

def emptySave():
    return {
        "playerData"   : {
            "savePrep" : None,
            "weapon"   : [],
            "layer"    : [1, 1],
            "money"    : 0,
            "inventory": [],
            "hp"       : 6,
            "MHP"      : 6
        },

        "worldData"     : {
            "layers"    : {},
            "difficulty": None
        },

        "metaData"        : {
            "visitedRooms": [(0, 0)]
        }
    }

def readSave():
    """
        return (
            playerData["savePrep"], #0
            generatedMap,           #1
            currentLayerID,         #2
            playerData["weapon"],   #3
            visitedRooms,           #4
            save,                   #5
            difficulty              #6
        )
    """
    if not os.path.exists(savePath):
        return False
    try:
        with open(savePath, "r") as file:
            save = json.load(file)

    except Exception as e:
        print("dataSaving load error:", e)
        return False
    try:
        playerData     = save["playerData"]
        worldData      = save["worldData"]
        metaData       = save["metaData"]
        currentLayerID = playerData["layer"]
        worldID        = str(currentLayerID[0])
        floorID        = str(currentLayerID[1])
        generatedMap   = (worldData["layers"][worldID][floorID])
        visitedRooms   = [tuple(x)for x in metaData["visitedRooms"]]
        difficulty     = save["worldData"]["difficulties"]


        print(
            playerData["savePrep"],  # 0
            generatedMap,  # 1
            currentLayerID,  # 2
            playerData["weapon"],  # 3
            visitedRooms,  # 4
            save,  # 5
            difficulty,
            playerData["money"],
            playerData["inventory"]

        )


        return (
            playerData["savePrep"], #0
            generatedMap,           #1
            currentLayerID,         #2
            playerData["weapon"],   #3
            visitedRooms,           #4
            save,                   #5
            difficulty,             #6
            playerData["money"],    #7
            playerData["inventory"],#8
            playerData["hp"],       #9
            playerData["MHP"]       #10
        )

    except Exception as e:
        print("dataSaving parse error:", e)
        return False

def getDifficulty(save):
    return save["worldData"]["difficulties"]

def getSavedMap(save, layerID):
    try:
        worldID = str(layerID[0])
        floorID = str(layerID[1])
        return (
            save["worldData"]["layers"]
            [worldID]
            [floorID]
        )

    except:
        return None


def deleteSave():
    try:
        os.remove(savePath)
        print("dataSaving: successfully deleted save")
    except FileNotFoundError:
        print("dataSaving: no save found, continuing")


def saveGameCall(currentLayerID, playerSavePrep, playerObj, worldCache, roomIDCompendium, difficulty):
    try:
        saveDat = {
            "playerData": {
                "savePrep": playerSavePrep,
                "weapon": [gun.__class__.__name__ for gun in playerObj.obtainedGuns],
                "layer": currentLayerID,
                "money":playerObj.money,
                "inventory": playerObj.inventory,
                "hp"       : playerObj.hp,
                "MHP"      : playerObj.maxHp
            },

            "worldData": {
                "layers": worldCache,
                "difficulties" : difficulty
            },

            "metaData": {
                "visitedRooms": roomIDCompendium
            }
        }
        with open(
            "data/gameSaveData/save.json",
            "w"
        ) as file:
            json.dump(
                saveDat,
                file,
                indent=4
            )
        print("datasavomngg: saved")
    except Exception as e:
        print("dataSaving: save error:", e)

def setHP():
    data = None
    with open(savePath, "r") as file:
        data = json.load(file)

        data["playerData"]["hp"] = 6767
        data["playerData"]["MHP"] = 6767

    with open(savePath, 'w') as file:
        json.dump(data, file, indent=4)