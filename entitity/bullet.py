import pygame

class bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, targetX, targetY, speed=500, size=(10, 10), color=(255, 220, 50), damage=1, owner=None):
        super().__init__()
        self.damage = damage
        self.owner  = owner #hit filtering purpose

        self.image = pygame.Surface(size, pygame.SRCALPHA)
        self.image.fill(color)
        self.rect       = self.image.get_rect(center=(x, y))
        self.posX       = float(x)
        self.posY       = float(y)

        direction = pygame.Vector2(targetX - x, targetY - y)
        if direction.length() > 0:
            direction = direction.normalize()
        self.velocity = direction * speed

    def update(self, deltaTime, screenW, screenH):
        self.posX      += self.velocity.x * deltaTime
        self.posY      += self.velocity.y * deltaTime
        self.rect.center = (self.posX, self.posY)

        if (self.rect.right < 0 or self.rect.left > screenW or
                self.rect.bottom < 0 or self.rect.top > screenH):
            self.kill()