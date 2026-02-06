import pygame
from settings import SCREEN_WIDTH
from graphics.colors import UI_TEXT, UI_HIGHLIGHT, UI_SCORE_POPUP, HEALTH_RED, HEALTH_GREEN


class ScorePopup:
    """Floating text that drifts upward and fades."""

    def __init__(self, text, x, y):
        self.text = text
        self.x = x
        self.y = y
        self.timer = 1.0  # seconds to live
        self.speed = 60   # px/s upward

    def update(self, dt):
        self.y -= self.speed * dt
        self.timer -= dt

    @property
    def alive(self):
        return self.timer > 0


class HUD:
    """Heads-up display: score, lives, floating popups."""

    def __init__(self):
        pygame.font.init()
        self.font = pygame.font.SysFont("Arial", 24, bold=True)
        self.popup_font = pygame.font.SysFont("Arial", 20, bold=True)
        self.popups = []

    def add_popup(self, text, x, y):
        self.popups.append(ScorePopup(text, x, y))

    def update(self, dt):
        for p in self.popups:
            p.update(dt)
        self.popups = [p for p in self.popups if p.alive]

    def draw(self, surface, score, lives):
        # Score (top left)
        score_surf = self.font.render(f"Score: {score}", True, UI_TEXT)
        surface.blit(score_surf, (15, 10))

        # Lives (top right) - draw as hearts
        lives_text = self.font.render(f"Lives: {lives}", True, UI_TEXT)
        surface.blit(lives_text, (SCREEN_WIDTH - 130, 10))

        # Popups (screen-space)
        for p in self.popups:
            alpha = max(0, min(255, int(255 * p.timer)))
            color = UI_SCORE_POPUP if "+" in p.text else UI_HIGHLIGHT
            popup_surf = self.popup_font.render(p.text, True, color)
            popup_surf.set_alpha(alpha)
            surface.blit(popup_surf, (p.x, p.y))
