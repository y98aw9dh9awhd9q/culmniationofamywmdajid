import pygame
import math

class sniperAIClass:
    def __init__(self, enemy, screen, difficulty):
        self.enemy      = enemy
        self.screen     = screen
        self.difficulty = difficulty
        self.state      = "reposition"
        self.timer      = 0
        self.beamActive = False
        self.beamStart  = (0, 0)
        self.beamEnd    = (0, 0)
        self.angle      = 0
        self.bullets    = pygame.sprite.Group()

    def update(self, dt, roomId, player):
        match self.state:
            case "reposition" : self.reposition(dt, roomId, player)
            case "aim"        : self.aim(       dt,         player)
            case "hold"       : self.hold(      dt                )
            case "fire"       : self.firePhase( dt                )

    def reposition(self, dt, roomId, player):
        ex, ey  = self.enemy.rect.center
        px, py  = player.rect.center
        dir     = pygame.Vector2(ex - px, ey - py)
        if dir.length() > 0:
            dir = dir.normalize()

        target  = pygame.Vector2(px, py) + dir * 400
        move    = target - pygame.Vector2(ex, ey)

        if move.length() > 10:
            self.enemy.moveAndCollide(move.normalize() * 200 * dt, roomId)
        else:
            self.state = "aim"
            self.timer = 0.6 / self.difficulty

    def aim(self, dt, player):
        ex, ey          = self.enemy.rect.center
        px, py          = player.rect.center
        self.angle      = math.atan2(py - ey, px - ex)
        self.beamActive = True
        self.updateBeam(ex, ey)

        self.timer    -= dt
        if self.timer <= 0:
            self.state = "hold"
            self.timer = 0.3 / self.difficulty

    def hold(self, dt):
        ex, ey = self.enemy.rect.center
        self.updateBeam(ex, ey)

        self.timer    -= dt
        if self.timer <= 0:
            self.state = "fire"
            self.timer = 0.25 / self.difficulty

    def firePhase(self, dt):
        ex, ey = self.enemy.rect.center

        self.updateBeam(ex, ey)

        self.timer         -= dt
        if self.timer      <= 0:
            self.beamActive = False
            self.state      = "reposition"

    def updateBeam(self, ex, ey):
        self.beamStart = (ex, ey)
        self.beamEnd   = (
            ex + math.cos(self.angle) * 3000,
            ey + math.sin(self.angle) * 3000
        )

    def beamHitsPlayer(self, player):
        if not self.beamActive or self.state != "fire":
            return False

        px, py = player.rect.center
        ax, ay = self.beamStart
        bx, by = self.beamEnd
        line   = pygame.Vector2(bx - ax, by - ay)
        point  = pygame.Vector2(px - ax, py - ay)

        if line.length_squared() == 0:
            return False

        #for your information mr nagra, T is a projection scalar and i just remember reading somewhere
        #that its the proper var or whatever
        t       = max(0, min(1, point.dot(line) / line.length_squared()))
        closest = pygame.Vector2(ax, ay) + line * t

        return pygame.Vector2(px, py).distance_to(closest) < 18

    def draw(self, screen):
        self.bullets.draw(screen)
        if self.beamActive:
            ex, ey    = self.beamStart
            bx, by    = self.beamEnd
            beam_surf = pygame.Surface(
                (self.enemy.screenW, self.enemy.screenH),
                pygame.SRCALPHA
            )

            pygame.draw.line(
                beam_surf,
                (255, 0, 0, 120),
                (ex, ey),
                (bx, by),
                9
            )

            if self.state == "fire":
                pygame.draw.line(
                    beam_surf,
                    (255, 0, 0),
                    (ex, ey),
                    (bx, by),
                    18
                )

            screen.blit(beam_surf, (0, 0))