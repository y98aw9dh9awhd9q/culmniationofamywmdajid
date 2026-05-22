"""
entity abstract method for inheritence
"""


import abc

class entity(abc.ABC):
    def __init__(self, posX, posY,hp, weapon, ai,spawnLoc, model):
        self.posX     = float(posX)
        self.posY     = float(posY)
        self.hp       = hp
        self.weapon   = weapon
        self.ai       = ai
        self.spawnLoc = spawnLoc
        self.model    = model


    @abc.abstractmethod
    def takeDamage(self):
        pass

    @abc.abstractmethod
    def inheritAI(self):
        pass