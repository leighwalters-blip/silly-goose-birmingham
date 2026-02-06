import math
import pygame
from settings import TRASH_CAN_POINTS, GRAVITY, MAX_FALL_SPEED
from graphics.colors import BIN_SILVER, BIN_DARK, BIN_RIM, BIN_LID
from engine.sounds import play as play_sound


class TrashCan:
    """Metal trash can - destructible with hockey stick."""

    WIDTH = 20
    HEIGHT = 28

    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, self.WIDTH, self.HEIGHT)
        self.alive = True
        self.vel_y = 0

        # Destruction animation
        self.destroying = False
        self.destroy_timer = 0
        self.pieces = []  # flying debris

    def get_hit(self, direction):
        """Smashed by the hockey stick."""
        if not self.alive or self.destroying:
            return
        self.destroying = True
        self.destroy_timer = 0.6
        play_sound("metal_crash")

        # Create debris pieces
        cx, cy = self.rect.centerx, self.rect.centery
        for i in range(6):
            angle = i * 60 + 15
            speed = 120 + i * 20
            vx = math.cos(math.radians(angle)) * speed * direction
            vy = -abs(math.sin(math.radians(angle))) * speed - 50
            size = 4 + (i % 3) * 2
            self.pieces.append([float(cx), float(cy), vx, vy, size])

    def update(self, dt, tiles):
        if self.destroying:
            self.destroy_timer -= dt
            # Update debris
            for p in self.pieces:
                p[2] *= 0.98  # friction
                p[3] += 500 * dt  # gravity on pieces
                p[0] += p[2] * dt
                p[1] += p[3] * dt
            if self.destroy_timer <= 0:
                self.alive = False
            return

        # Gravity so cans settle on ground
        self.vel_y += GRAVITY * dt
        if self.vel_y > MAX_FALL_SPEED:
            self.vel_y = MAX_FALL_SPEED
        self.rect.y += int(self.vel_y * dt)
        for tile in tiles:
            if self.rect.colliderect(tile.rect):
                if self.vel_y > 0:
                    self.rect.bottom = tile.rect.top
                    self.vel_y = 0

    def draw(self, surface, camera):
        if not self.alive and not self.destroying:
            return

        sr = camera.apply(self.rect)
        if sr.right < -50 or sr.left > surface.get_width() + 50:
            return

        if self.destroying:
            # Draw flying debris
            alpha = max(0, min(255, int(255 * self.destroy_timer / 0.6)))
            for p in self.pieces:
                px = int(p[0]) - int(camera.offset_x if hasattr(camera, 'offset_x') else 0)
                py = int(p[1]) - int(camera.offset_y if hasattr(camera, 'offset_y') else 0)
                color = BIN_SILVER if p[4] > 5 else BIN_DARK
                pygame.draw.rect(surface, color, (px, py, p[4], p[4]))
            return

        # Bin body (tapered - wider at top)
        body_top = sr.y + 6
        body_bottom = sr.bottom
        body_h = body_bottom - body_top
        # Main body
        pygame.draw.rect(surface, BIN_SILVER, (sr.x + 1, body_top, sr.width - 2, body_h))
        # Darker side shading
        pygame.draw.rect(surface, BIN_DARK, (sr.x + 1, body_top, 4, body_h))
        # Horizontal ridges
        for ry in range(body_top + 5, body_bottom - 3, 6):
            pygame.draw.line(surface, BIN_DARK, (sr.x + 2, ry), (sr.right - 3, ry), 1)
        # Rim at top
        pygame.draw.rect(surface, BIN_RIM, (sr.x, body_top - 2, sr.width, 4))
        # Lid
        pygame.draw.ellipse(surface, BIN_LID, (sr.x - 1, sr.y, sr.width + 2, 8))
        # Lid handle
        pygame.draw.rect(surface, BIN_DARK, (sr.centerx - 3, sr.y - 2, 6, 3))

    @property
    def score_value(self):
        return TRASH_CAN_POINTS
