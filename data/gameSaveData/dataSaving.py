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
            "layers": {}
        },

        "metaData": {
            "visitedRooms": [(0, 0)]
        }
    }

def saveData(playerSavePrep, currentLayerID, weapon, entrances, generatedMap):
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

        with open(savePath, "w") as file:
            json.dump(save, file, indent=4)
        print("dataSaving: save successful")
    except Exception as e:
        print("dataSaving:", e)


def readSave():
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
        visitedRooms = [tuple(x)for x in metaData["visitedRooms"]]

        return (
            playerData["savePrep"],
            generatedMap,
            currentLayerID,
            playerData["weapon"],
            visitedRooms,
            save
        )

    except Exception as e:
        print("dataSaving parse error:", e)
        return False

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

def saveMapOnly(save, layerID, generatedMap):
    worldID = str(layerID[0])
    floorID = str(layerID[1])
    if worldID not in save["worldData"]["layers"]:
        save["worldData"]["layers"][worldID] = {}
    save["worldData"]["layers"][worldID][floorID] = generatedMap
    with open(savePath, "w") as file:
        json.dump(save, file, indent=4)


def deleteSave():
    try:
        os.remove(savePath)
        print("dataSaving: successfully deleted save")
    except FileNotFoundError:
        print("dataSaving: no save found, continuing")


def saveGameCall(currentLayerID,playerSavePrep,playerObj,worldCache,roomIDCompendium):
    try:
        saveDat = {
            "playerData": {
                "savePrep": playerSavePrep,
                "weapon": playerObj.obtainedGuns,
                "layer": currentLayerID
            },

            "worldData": {
                "layers": worldCache
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