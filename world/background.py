import pygame
from settings import SCREEN_WIDTH, SCREEN_HEIGHT
from graphics.colors import (
    SKY_TOP, SKY_BOTTOM, SILHOUETTE_FAR, SILHOUETTE_MID,
    TERRACE_COLOUR, LAMP_GLOW, LAMPPOST_GREY, PUB_WINDOW_GLOW
)


class Background:
    """Parallax Birmingham night-sky background."""

    def __init__(self):
        self.surface = self._build()

    def _build(self):
        surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))

        # Gradient sky
        for y in range(SCREEN_HEIGHT):
            t = y / SCREEN_HEIGHT
            r = int(SKY_TOP[0] + (SKY_BOTTOM[0] - SKY_TOP[0]) * t)
            g = int(SKY_TOP[1] + (SKY_BOTTOM[1] - SKY_TOP[1]) * t)
            b = int(SKY_TOP[2] + (SKY_BOTTOM[2] - SKY_TOP[2]) * t)
            pygame.draw.line(surf, (r, g, b), (0, y), (SCREEN_WIDTH, y))

        # Far silhouette (Birmingham skyline hints)
        points = [
            (0, 320), (60, 290), (80, 295), (100, 260),
            (130, 265), (160, 240), (170, 242), (180, 220),  # BT Tower hint
            (190, 242), (200, 260), (240, 270), (300, 280),
            (340, 260), (380, 265), (420, 250), (460, 255),
            (500, 270), (550, 265), (600, 280), (640, 270),
            (700, 285), (750, 275), (800, 290), (800, 400), (0, 400)
        ]
        pygame.draw.polygon(surf, SILHOUETTE_FAR, points)

        # Mid silhouette (terraced houses)
        for x in range(0, SCREEN_WIDTH, 60):
            h = 340 + (x * 7 % 30) - 15
            pygame.draw.rect(surf, SILHOUETTE_MID, (x, h, 58, 400 - h))
            # Chimney
            pygame.draw.rect(surf, SILHOUETTE_MID, (x + 10, h - 15, 8, 15))
            # Lit windows
            if x % 120 < 60:
                pygame.draw.rect(surf, PUB_WINDOW_GLOW, (x + 12, h + 15, 10, 10))
                pygame.draw.rect(surf, PUB_WINDOW_GLOW, (x + 35, h + 15, 10, 10))

        # Street lamps
        for lx in [150, 450, 700]:
            pygame.draw.rect(surf, LAMPPOST_GREY, (lx, 360, 4, 40))
            pygame.draw.circle(surf, LAMP_GLOW, (lx + 2, 358), 8)
            # Glow effect
            glow = pygame.Surface((30, 30), pygame.SRCALPHA)
            pygame.draw.circle(glow, (*LAMP_GLOW, 40), (15, 15), 15)
            surf.blit(glow, (lx - 13, 345))

        return surf

    def draw(self, surface, camera):
        # Parallax: background scrolls slower than foreground
        parallax_x = int(camera.offset_x * 0.3) % SCREEN_WIDTH
        surface.blit(self.surface, (-parallax_x, 0))
        surface.blit(self.surface, (SCREEN_WIDTH - parallax_x, 0))
