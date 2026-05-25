mapDelta = {
    0: (-1,  0),
    1: ( 1,  0),
    2: ( 0, -1),
    3: ( 0,  1),
}

oppositeSide = {
    0: 1,
    1: 0,
    2: 3,
    3: 2
}
from mapping.maps import getExitTiles
def getMatchingEntrance(roomID,comingFromDir,screenW,screenH,prevCenter):
    exits = getExitTiles(
        roomID,
        screenW,
        screenH
    )
    targetDir = oppositeSide[comingFromDir]
    candidates = [rect for rect, d in exits if d == targetDir]

    if not candidates:
        return None

    return min(
        candidates,
        key=lambda r:
        (r.centerx - prevCenter[0]) ** 2 +
        (r.centery - prevCenter[1]) ** 2
    )

def roomIDer(roomX, roomY, roomIDCompendium,reset=False):
    print(f"roomDirHelper: {roomIDCompendium} ")
    if reset:
        print("roomDirHelper: RESET")
        roomIDCompendium = [(0, 0)]
    t = (roomX, roomY)
    if t not in roomIDCompendium:
        roomIDCompendium.append(t)
        print(f"roomDIRHELPER: {roomIDCompendium} NEW ROOM")
        return "NEW"
    print(f"roomDirHelper: {roomIDCompendium} OLD ROOM")
    return "OLD"

def placePlayerAtDoor(playerObj,doorRect,comingFromDir):
    px, py                     = playerObj.rect.center

    if comingFromDir          == 0:
        playerObj.rect.centerx = px
        playerObj.rect.bottom  = doorRect.top - 1

    elif comingFromDir == 1:
        playerObj.rect.centerx = px
        playerObj.rect.top     = doorRect.bottom + 1

    elif comingFromDir == 2:
        playerObj.rect.centery = py
        playerObj.rect.right   = doorRect.left - 1

    elif comingFromDir == 3:
        playerObj.rect.centery = py
        playerObj.rect.left    = doorRect.right + 1