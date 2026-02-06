import pygame
from settings import SCREEN_WIDTH, SCREEN_HEIGHT
from graphics.colors import (
    UI_BG, UI_TEXT, UI_HIGHLIGHT, SKY_TOP,
    GOOSE_WHITE, GOOSE_BEAK_ORANGE, PUB_SIGN_TEXT
)


class Menu:
    """Title, game-over, and level-complete screens."""

    def __init__(self):
        self.font_large = None
        self.font_medium = None
        self.font_small = None
        self._init_fonts()

    def _init_fonts(self):
        pygame.font.init()
        self.font_large = pygame.font.SysFont("Arial", 64, bold=True)
        self.font_medium = pygame.font.SysFont("Arial", 36)
        self.font_small = pygame.font.SysFont("Arial", 24)

    def _draw_centered(self, surface, text, font, color, y):
        rendered = font.render(text, True, color)
        rect = rendered.get_rect(center=(SCREEN_WIDTH // 2, y))
        surface.blit(rendered, rect)

    def draw_title(self, surface):
        surface.fill(SKY_TOP)

        # Draw a simple goose silhouette
        cx, cy = SCREEN_WIDTH // 2, 200
        # Body
        pygame.draw.ellipse(surface, GOOSE_WHITE, (cx - 40, cy - 15, 80, 40))
        # Neck
        pygame.draw.ellipse(surface, GOOSE_WHITE, (cx + 20, cy - 55, 20, 50))
        # Head
        pygame.draw.circle(surface, GOOSE_WHITE, (cx + 35, cy - 55), 14)
        # Beak
        pygame.draw.polygon(surface, GOOSE_BEAK_ORANGE, [
            (cx + 48, cy - 58), (cx + 65, cy - 55), (cx + 48, cy - 52)
        ])

        self._draw_centered(surface, "SILLY GOOSE", self.font_large, PUB_SIGN_TEXT, 300)
        self._draw_centered(surface, "Birmingham Streets", self.font_medium, UI_TEXT, 360)
        self._draw_centered(surface, "Press ENTER to start", self.font_small, UI_HIGHLIGHT, 450)
        self._draw_centered(surface, "Arrows/WASD: Move   Space: Jump   X/Z: Hit", self.font_small, UI_TEXT, 500)
        self._draw_centered(surface, "ESC: Quit", self.font_small, UI_TEXT, 535)

    def draw_game_over(self, surface, score):
        surface.fill(UI_BG)
        self._draw_centered(surface, "GAME OVER", self.font_large, UI_HIGHLIGHT, 200)
        self._draw_centered(surface, f"Score: {score}", self.font_medium, UI_TEXT, 300)
        self._draw_centered(surface, "Press ENTER for menu", self.font_small, UI_TEXT, 400)

    def draw_level_complete(self, surface, next_level, score):
        surface.fill(UI_BG)
        self._draw_centered(surface, "LEVEL COMPLETE!", self.font_large, UI_HIGHLIGHT, 200)
        self._draw_centered(surface, f"Score: {score}", self.font_medium, UI_TEXT, 300)
        self._draw_centered(surface, f"Press ENTER for Level {next_level + 1}", self.font_small, UI_TEXT, 400)
