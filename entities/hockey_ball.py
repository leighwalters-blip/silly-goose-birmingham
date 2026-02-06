import pygame
from settings import BALL_HIT_SPEED, BALL_FRICTION, BALL_GRAVITY
from graphics.colors import BALL_WHITE
from engine.sounds import play as play_sound


class HockeyBall:
    """Physics ball that the goose can whack with the stick."""

    RADIUS = 6

    def __init__(self, x, y):
        self.rect = pygame.Rect(x - self.RADIUS, y - self.RADIUS,
                                self.RADIUS * 2, self.RADIUS * 2)
        self.vel_x = 0
        self.vel_y = 0
        self.on_ground = False

    def get_hit(self, direction):
        """Called when player swings stick at this ball."""
        self.vel_x = BALL_HIT_SPEED * direction
        self.vel_y = -BALL_HIT_SPEED * 0.4
        self.on_ground = False
        play_sound("stick_hit")

    def update(self, dt, tiles):
        # Gravity
        self.vel_y += BALL_GRAVITY * dt

        # Friction
        self.vel_x *= BALL_FRICTION

        # Stop if very slow
        if abs(self.vel_x) < 5:
            self.vel_x = 0

        # Move X
        self.rect.x += int(self.vel_x * dt)
        for tile in tiles:
            if self.rect.colliderect(tile.rect):
                if self.vel_x > 0:
                    self.rect.right = tile.rect.left
                elif self.vel_x < 0:
                    self.rect.left = tile.rect.right
                self.vel_x = -self.vel_x * 0.5
                break

        # Move Y
        self.on_ground = False
        self.rect.y += int(self.vel_y * dt)
        for tile in tiles:
            if self.rect.colliderect(tile.rect):
                if self.vel_y > 0:
                    self.rect.bottom = tile.rect.top
                    self.on_ground = True
                elif self.vel_y < 0:
                    self.rect.top = tile.rect.bottom
                self.vel_y = -self.vel_y * 0.3
                break

    def draw(self, surface, camera):
        sr = camera.apply(self.rect)
        if sr.right < 0 or sr.left > surface.get_width():
            return
        center = (sr.centerx, sr.centery)
        pygame.draw.circle(surface, BALL_WHITE, center, self.RADIUS)
        pygame.draw.circle(surface, (200, 200, 200), center, self.RADIUS, 1)
