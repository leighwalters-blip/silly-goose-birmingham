import pygame
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, TILE_SIZE


class Camera:
    """Side-scrolling camera that follows the player."""

    def __init__(self, level_width, level_height):
        self.offset_x = 0
        self.offset_y = 0
        self.level_width = level_width
        self.level_height = level_height

    def update(self, target_rect):
        # Center on target horizontally
        self.offset_x = target_rect.centerx - SCREEN_WIDTH // 2
        # Keep camera slightly above center vertically
        self.offset_y = target_rect.centery - SCREEN_HEIGHT // 2 - 50

        # Clamp to level bounds
        self.offset_x = max(0, min(self.offset_x, self.level_width - SCREEN_WIDTH))
        self.offset_y = max(0, min(self.offset_y, self.level_height - SCREEN_HEIGHT))

    def apply(self, rect):
        """Return a new rect shifted by camera offset."""
        return pygame.Rect(rect.x - self.offset_x, rect.y - self.offset_y,
                           rect.width, rect.height)

    def apply_pos(self, x, y):
        """Return screen position for world coordinates."""
        return (x - self.offset_x, y - self.offset_y)
