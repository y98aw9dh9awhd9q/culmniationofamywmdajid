import time
import pygame

prRawCache = {}

def preload(path):
    if path not in prRawCache:
        prRawCache[path] = pygame.image.load_animation(path)

class animatedGif:
    def __init__(self, path, targetSize):
        if path not in prRawCache:
            preload(path)
        rawFrames = prRawCache[path]
        self.prFrames = []
        for surf, durationMs in rawFrames:
            scaled = pygame.transform.scale(surf, targetSize)
            self.prFrames.append([scaled, durationMs / 1000.0])
        self.prTotal = len(self.prFrames)
        self.prIndex = 0
        self.prLastTime = 0.0

    def blitReady(self):
        now = time.time()
        if self.prLastTime == 0:
            self.prLastTime = now
        elapsed = now - self.prLastTime
        if elapsed >= self.prFrames[self.prIndex][1]:
            self.prIndex = (self.prIndex + 1) % self.prTotal
            self.prLastTime = now
        return self.prFrames[self.prIndex][0]

    def reset(self):
        self.prIndex = 0
        self.prLastTime = 0.0
