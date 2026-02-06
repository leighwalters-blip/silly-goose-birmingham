import pygame
from settings import TILE_SIZE
from graphics.colors import (
    GROUND_COLOUR, PLATFORM_COLOUR, BRICK_RED, BRICK_DARK,
    BRICK_MORTAR, KERB_COLOUR
)


# Tile types
EMPTY = 0
GROUND = 1
PLATFORM = 2
BRICK = 3
KERB = 4


class Tile:
    """Single tile in the world."""

    def __init__(self, tile_type, grid_x, grid_y):
        self.tile_type = tile_type
        self.rect = pygame.Rect(
            grid_x * TILE_SIZE, grid_y * TILE_SIZE,
            TILE_SIZE, TILE_SIZE
        )

    def draw(self, surface, camera):
        screen_rect = camera.apply(self.rect)
        # Skip if off screen
        if screen_rect.right < 0 or screen_rect.left > surface.get_width():
            return
        if screen_rect.bottom < 0 or screen_rect.top > surface.get_height():
            return

        if self.tile_type == GROUND:
            pygame.draw.rect(surface, GROUND_COLOUR, screen_rect)
            # Top edge highlight
            pygame.draw.line(surface, KERB_COLOUR,
                             screen_rect.topleft, screen_rect.topright, 2)
        elif self.tile_type == PLATFORM:
            pygame.draw.rect(surface, PLATFORM_COLOUR, screen_rect)
            pygame.draw.rect(surface, KERB_COLOUR, screen_rect, 1)
        elif self.tile_type == BRICK:
            pygame.draw.rect(surface, BRICK_RED, screen_rect)
            # Draw brick pattern
            half = TILE_SIZE // 2
            quarter = TILE_SIZE // 4
            # Horizontal mortar lines
            pygame.draw.line(surface, BRICK_MORTAR,
                             (screen_rect.x, screen_rect.y + half),
                             (screen_rect.right, screen_rect.y + half), 1)
            # Vertical mortar lines (offset pattern)
            pygame.draw.line(surface, BRICK_MORTAR,
                             (screen_rect.x + half, screen_rect.y),
                             (screen_rect.x + half, screen_rect.y + half), 1)
            pygame.draw.line(surface, BRICK_MORTAR,
                             (screen_rect.x + quarter, screen_rect.y + half),
                             (screen_rect.x + quarter, screen_rect.bottom), 1)
            pygame.draw.line(surface, BRICK_MORTAR,
                             (screen_rect.x + half + quarter, screen_rect.y + half),
                             (screen_rect.x + half + quarter, screen_rect.bottom), 1)
        elif self.tile_type == KERB:
            pygame.draw.rect(surface, KERB_COLOUR, screen_rect)
            pygame.draw.rect(surface, GROUND_COLOUR, screen_rect, 1)
