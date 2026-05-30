import random
import uuid

chestLoot = {
    0: ["basicPistol"],
    1: ["burstRifle", "shotgun"]
}

class chest:
    def __init__(self, layerID):
        self.opened = False
        self.layerID = layerID
        self.uuid = uuid.uuid4()

    def generateChestLoot(self):
        layerID = self.layerID[0]
        print(f"chestLogic: generating chest loot from layer {layerID}")
        generatedLoot = random.choice(chestLoot[layerID])
        return generatedLoot

    def openChest(self):
        if not self.opened:
            print("chestLogic: opened chest", self.layerID)
            self.opened = True
            return self.generateChestLoot()
        return None
