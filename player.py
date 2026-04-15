from const import playerDir
import pygame

class player:
    immuFrameTime = 0.5
    def __init__(self,screen):
        self.screen = screen
        self.hp = 3
        self.image = pygame.image.load(playerDir)
        self.image = pygame.transform.scale(self.image, (100, 100))
        self.rect = self.image.get_rect()
        self.speed = 200
        self.invincibilityTimer = 0
        self.dx, self.dy = 0, 0
        screen.blit(self.image, (self.rect.x, self.rect.y))

    def takeDamage(self):
        if self.invincibilityTimer > 0:
            return
        self.hp -= 1
        self.invincibilityTimer = self.immuFrameTime

    def update(self, deltaTime):

        if self.invincibilityTimer > 0:
            self.invincibilityTimer -= deltaTime


        key = pygame.key.get_pressed()
        if pygame.event == pygame.KEYDOWN:
            if key[pygame.K_a]:
                self.dx -= 4
            if key[pygame.K_d]:
                self.dx += 4
            if key[pygame.K_w]:
                self.dy -= 4
            if key[pygame.K_s]:
                self.dy += 4

        velocity = pygame.Vector2(self.dx, self.dy)
        if velocity.length() > 0:
            velocity = velocity.normalize() * self.speed * deltaTime

        self.rect.x += velocity.x
        self.rect.y += velocity.y
        print(velocity.x)
        self.screen.blit(self.image, self.rect)
        pygame.display.flip()

