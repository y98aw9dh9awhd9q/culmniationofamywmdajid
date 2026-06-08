import pygame

class musManager:
    def __init__(self):
        self.tracks           = {}
        self.currentType      = None
        self.currentStartTick = 0

    def registerTrack(self, trackType, path):
        self.tracks[trackType] = {
            "path": path,
            "position": 0.0,
            "playing": False
        }






    def prElapsed(self):
        return (pygame.time.get_ticks() - self.currentStartTick) / 1000.0

    def prStopCurrent(self):
        if self.currentType is None:
            return

        track              = self.tracks[self.currentType]

        track["position"] += self.prElapsed()
        track["playing"]   = False

        pygame.mixer.music.stop()

        self.currentType   = None

    def prPlay(self, trackType):
        if trackType not in self.tracks:
            print(f"musicManager: missing track {trackType}")
            return

        if self.currentType == trackType:
            return

        self.prStopCurrent()

        track = self.tracks[trackType]

        pygame.mixer.music.load(track["path"])

        try:
            pygame.mixer.music.play(loops=-1, start=track["position"])
        except Exception:
            pygame.mixer.music.play(-1)

        track["playing"] = True

        self.currentType = trackType
        self.currentStartTick = pygame.time.get_ticks()








    def startCombat(self):
        self.prPlay("combat")

    def stopCombat(self):
        if self.currentType == "combat":
            self.prStopCurrent()







    def startShop(self):
        self.prPlay("shop")

    def stopShop(self):
        if self.currentType == "shop":
            self.prStopCurrent()









    def startBoss(self, bossName):
        self.prPlay("boss" + bossName[0].upper() + bossName[1:])

    def stopBoss(self):
        if (
            self.currentType is not None
            and self.currentType.startswith("boss")
        ):
            self.prStopCurrent()








    def stopAll(self):
        self.prStopCurrent()

    def reset(self):
        pygame.mixer.music.stop()

        for track in self.tracks.values():
            track["position"] = 0.0
            track["playing"] = False

        self.currentType = None
        self.currentStartTick = 0