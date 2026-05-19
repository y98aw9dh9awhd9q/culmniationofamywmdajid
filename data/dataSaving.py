import json
import os

def saveData(dataToSave):
        try:
            playerSavePrep, generatedMap, currentLayerID = dataToSave
            print(playerSavePrep)
            print(generatedMap)
            print(currentLayerID)
            dataToDump = {
                "playerSaveData" : playerSavePrep,
                "generatedMap" : generatedMap,
                "currentLayerID" : currentLayerID
            }
            with open("data/save.json","w") as file:
                json.dump(dataToDump,file)
        except:

            dataToDump = {
                "playerSaveData" :   None,
                "generatedMap"   :   None,
                "currentLayerID" :   None
            }
            with open("data/save.json", "w") as file:
                json.dump(dataToDump, file)
"""
example saved data for ref
{"playerSaveData": [33, 1, 0, [91, 300]],
  "generatedMap": [[-1, 33, 19], [3, 2, 1], [17, -3, -2]], 
  "currentLayerID": [1, 5]}
"""

def readSave():
    try:
        with open("data/save.json","r") as file:
            loadedData = json.load(file)
    except:
        return False
    playerSaveData = loadedData["playerSaveData"]
    generatedMap = loadedData["generatedMap"]
    currentLayerID = loadedData["currentLayerID"]
    return playerSaveData, generatedMap, currentLayerID

def deleteSave():
    try:
        os.remove("data/save.json")
        print("dataSaving: successfully deleted save")
    except FileNotFoundError:
        print("no save found, continuing")