import json
import os

savePath = "data/gameSaveData/save.json"

def emptySave():
    return {
        "playerData": {
            "savePrep": None,
            "weapon": [],
            "layer": [1, 1]
        },

        "worldData": {
            "layers": {},
            "difficulty": None
        },

        "metaData": {
            "visitedRooms": [(0, 0)]
        }
    }

def saveData(playerSavePrep, currentLayerID, weapon, entrances, generatedMap, difficulty):
    try:
        if os.path.exists(savePath):
            with open(savePath, "r") as file:
                save                     = json.load(file)
        else:
            save                         = emptySave()
        worldLayers                      = save["worldData"]["layers"]
        worldID                          = str(currentLayerID[0])
        floorID                          = str(currentLayerID[1])

        if worldID not in worldLayers:
            worldLayers[worldID]         = {}

        worldLayers[worldID][floorID]    = generatedMap

        save["playerData"]["savePrep"]   = playerSavePrep
        save["playerData"]["weapon"]     = weapon
        save["playerData"]["layer"]      = currentLayerID
        save["metaData"]["visitedRooms"] = entrances
        save["worldData"]["difficulty"]  = difficulty

        with open(savePath, "w") as file:
            json.dump(save, file, indent=4)
        print("dataSaving: save successful")
    except Exception as e:
        print("dataSaving:", e)


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
            difficulty
        )
        return (
            playerData["savePrep"], #0
            generatedMap,           #1
            currentLayerID,         #2
            playerData["weapon"],   #3
            visitedRooms,           #4
            save,                   #5
            difficulty              #6
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
                "weapon": playerObj.obtainedGuns,
                "layer": currentLayerID
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
