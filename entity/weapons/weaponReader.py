import json
import const
import os

class weapon():
    def __init__(self, identification):
        self.damage = 0
        self.cooldown = 0
        self.identificationPass = identification
        self.datLoaded = ""


        #identification
        # gun type (PISTOL)
        # gun ID (#)
        # exmaple ID (PISTOL#1)
        self.identification = self.identificationPass.partition("#")  # (left, partition, right)

    def readWeaponSheet(self):
        with open(os.path.join(
            const.baseDir,
            "entity",
            "weapons",
            f"{self.identification[0]}.json"
        ), "r") as file:
            loadedDat = json.load(file)
            self.datLoaded = loadedDat[self.identification[2]]


        self.cooldown = self.datLoaded["CD"]
        self.damage = self.datLoaded["DMG"]
