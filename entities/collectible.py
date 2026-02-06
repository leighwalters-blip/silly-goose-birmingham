import math
import pygame
from settings import BEER_POINTS, CIDER_POINTS, BOB_SPEED, BOB_AMPLITUDE
from graphics.colors import (
    BEER_AMBER, BEER_FOAM, BEER_GLASS,
    CIDER_GREEN, CIDER_DARK_GREEN, CIDER_GOLD_CAP
)


class Collectible:
    """Bobbing pickup - beer or cider."""

    WIDTH = 16
    HEIGHT = 20

    def __init__(self, x, y, kind="beer"):
        self.base_y = y
        self.rect = pygame.Rect(x, y, self.WIDTH, self.HEIGHT)
        self.kind = kind
        self.points = BEER_POINTS if kind == "beer" else CIDER_POINTS
        self.alive = True
        self.bob_timer = 0

    def update(self, dt):
        if not self.alive:
            return
        self.bob_timer += dt * BOB_SPEED
        self.rect.y = self.base_y + int(math.sin(self.bob_timer) * BOB_AMPLITUDE)

    def collect(self, game):
        if not self.alive:
            return
        self.alive = False
        game.add_score(self.points, self.rect.centerx, self.rect.y)

    def draw(self, surface, camera):
        if not self.alive:
            return

        sr = camera.apply(self.rect)
        if sr.right < 0 or sr.left > surface.get_width():
            return

        if self.kind == "beer":
            # Pint glass
            pygame.draw.rect(surface, BEER_GLASS, (sr.x + 2, sr.y + 4, 12, 16))
            # Beer liquid
            pygame.draw.rect(surface, BEER_AMBER, (sr.x + 3, sr.y + 6, 10, 12))
            # Foam
            pygame.draw.rect(surface, BEER_FOAM, (sr.x + 3, sr.y + 4, 10, 4))
            # Handle
            pygame.draw.rect(surface, BEER_GLASS, (sr.x + 13, sr.y + 8, 3, 8))
        else:
            # Cider bottle
            pygame.draw.rect(surface, CIDER_GREEN, (sr.x + 4, sr.y + 6, 8, 14))
            # Neck
            pygame.draw.rect(surface, CIDER_DARK_GREEN, (sr.x + 5, sr.y + 2, 6, 6))
            # Cap
            pygame.draw.rect(surface, CIDER_GOLD_CAP, (sr.x + 5, sr.y, 6, 3))
            # Label
            pygame.draw.rect(surface, (255, 255, 255), (sr.x + 5, sr.y + 10, 6, 4))
