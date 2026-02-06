import pygame
from settings import GOAL_POINTS, TILE_SIZE
from graphics.colors import GOAL_NET, GOAL_POST


class Goal:
    """End-of-level hockey goal."""

    WIDTH = TILE_SIZE * 2
    HEIGHT = TILE_SIZE * 2

    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, self.WIDTH, self.HEIGHT)
        self.reached = False

    def reach_goal(self, game):
        if self.reached:
            return
        self.reached = True
        game.add_score(GOAL_POINTS, self.rect.centerx, self.rect.y)
        game.complete_level()

    def draw(self, surface, camera):
        sr = camera.apply(self.rect)
        if sr.right < 0 or sr.left > surface.get_width():
            return

        # Posts
        pygame.draw.rect(surface, GOAL_POST, (sr.x, sr.y, 4, sr.height))
        pygame.draw.rect(surface, GOAL_POST, (sr.right - 4, sr.y, 4, sr.height))
        # Crossbar
        pygame.draw.rect(surface, GOAL_POST, (sr.x, sr.y, sr.width, 4))
        # Net (grid lines)
        for nx in range(sr.x + 8, sr.right - 4, 10):
            pygame.draw.line(surface, GOAL_NET, (nx, sr.y + 4), (nx, sr.bottom), 1)
        for ny in range(sr.y + 8, sr.bottom, 10):
            pygame.draw.line(surface, GOAL_NET, (sr.x + 4, ny), (sr.right - 4, ny), 1)
