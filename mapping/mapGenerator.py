import random
from mapping.maps import normalPool

totalLayers  = 9
roomsPerLayer = 4

def layerGridSize(layerNum):
    return 2 + layerNum

def buildSequence(seed=None):
    rng = random.Random(seed)
    sequence = []

    for layerNum in range(1, totalLayers + 1):
        for roomNum in range(1, roomsPerLayer + 1):
            isBoss     = (roomNum == roomsPerLayer)
            isEntrance = (roomNum == 1)
            isExit     = isBoss

            if isEntrance:
                roomId = "entrance"
            elif isBoss:
                roomId = "boss"
            elif roomNum == 2:
                roomId = "shop"
            else:
                roomId = rng.choice(normalPool)

            sequence.append({
                "layerNum":   layerNum,
                "roomNum":    roomNum,
                "roomId":     roomId,
                "isBoss":     isBoss,
                "isEntrance": isEntrance,
                "isExit":     isExit,
            })

    sequence[-1]["roomId"] = "exit"
    sequence[-1]["isExit"] = True

    return sequence

def getRoomInfo(sequence, index):
    if 0 <= index < len(sequence):
        return sequence[index]
    return None

def formatLabel(info):
    if info is None:
        return "---"
    return f"{info['layerNum']}-{info['roomNum']}  [{info['roomId']}]"

if __name__ == "__main__":
    seq = buildSequence()
    for i, info in enumerate(seq):
        tag = ""
        if info["isEntrance"]: tag += " <ENTRANCE>"
        if info["isBoss"]:     tag += " <BOSS>"
        if info["isExit"] and info["layerNum"] == totalLayers: tag += " <FINAL>"
        print(f"  [{i:02d}] {info['layerNum']}-{info['roomNum']}  {info['roomId']:<12}{tag}")
    print(f"\n  Total rooms: {len(seq)}")