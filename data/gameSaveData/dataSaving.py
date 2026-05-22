import json
import os

def saveData(dataToSave):
        try:
            playerSavePrep, generatedMap, currentLayerID,weapon,entrances = dataToSave
            print(playerSavePrep)
            print(generatedMap)
            print(currentLayerID)
            print(weapon)
            dataToDump = {
                "playerSaveData" : playerSavePrep,
                "generatedMap"   : generatedMap,
                "currentLayerID" : currentLayerID,
                "weapon"         : weapon,
                "savedEntrances" : entrances
            }
            with open("data/gameSaveData/save.json","w") as file:
                json.dump(dataToDump,file)
        except Exception as e:
            print(f"dataSaving: {e}")
            dataToDump = {
                "playerSaveData" :   None,
                "generatedMap"   :   None,
                "currentLayerID" :   None,
                "weapon"         :   None,
                "savedEntrances" :   None
            }
            with open("data/gameSaveData/save.json", "w") as file:
                json.dump(dataToDump, file)
"""
example saved data for ref
{"playerSaveData": [33, 1, 0, [91, 300]],
  "generatedMap": [[-1, 33, 19], [3, 2, 1], [17, -3, -2]], 
  "currentLayerID": [1, 5],
  "weapon: "pistol#1""}
"""

def readSave():
    returnEntrances = []
    try:
        with open("data/gameSaveData/save.json","r") as file:
            loadedData = json.load(file)
    except:
        return False
    playerSaveData = loadedData["playerSaveData"]
    generatedMap   = loadedData["generatedMap"]
    currentLayerID = loadedData["currentLayerID"]
    weapon         = loadedData["weapon"]
    savedEntrances = loadedData["savedEntrances"]
    for item in savedEntrances:
        returnEntrances.append(tuple(item))
    print("dataSaving: entrances" , returnEntrances)
    return playerSaveData, generatedMap, currentLayerID, weapon,returnEntrances

def deleteSave():
    try:
        os.remove("data/gameSaveData/save.json")
        print("dataSaving: successfully deleted save")
    except FileNotFoundError:
        print("no save found, continuing")