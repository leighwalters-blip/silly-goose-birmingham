import pygame
from settings import RAT_SPEED, TILE_SIZE
from graphics.colors import RAT_GREY, RAT_DARK, RAT_PINK, RAT_EYE_RED, RAT_WHISKER


class Rat:
    """Patrol enemy - walks back and forth on platforms."""

    WIDTH = 24
    HEIGHT = 16
    damage = True  # flag for player collision detection

    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, self.WIDTH, self.HEIGHT)
        self.speed = RAT_SPEED
        self.facing_right = True
        self.alive = True
        self.walk_timer = 0

    def update(self, dt, tiles):
        if not self.alive:
            return

        self.walk_timer += dt * 6

        # Move horizontally
        self.rect.x += int(self.speed * dt)

        # Check wall collisions
        hit_wall = False
        for tile in tiles:
            if self.rect.colliderect(tile.rect):
                if self.speed > 0:
                    self.rect.right = tile.rect.left
                else:
                    self.rect.left = tile.rect.right
                hit_wall = True
                break

        # Check if about to walk off edge
        if not hit_wall:
            test_x = self.rect.right + 2 if self.speed > 0 else self.rect.left - 2
            test_rect = pygame.Rect(test_x, self.rect.bottom + 2, 4, 4)
            has_ground = any(test_rect.colliderect(t.rect) for t in tiles)
            if not has_ground:
                hit_wall = True

        if hit_wall:
            self.speed = -self.speed
            self.facing_right = self.speed > 0

    def draw(self, surface, camera):
        if not self.alive:
            return

        sr = camera.apply(self.rect)
        if sr.right < 0 or sr.left > surface.get_width():
            return

        flip = not self.facing_right

        # Body
        pygame.draw.ellipse(surface, RAT_GREY, sr)

        # Head
        head_x = sr.right - 6 if not flip else sr.left - 2
        pygame.draw.ellipse(surface, RAT_DARK,
                            (head_x, sr.y + 1, 10, 10))

        # Ear
        ear_x = head_x + 6 if not flip else head_x + 1
        pygame.draw.circle(surface, RAT_PINK, (ear_x, sr.y + 2), 3)

        # Eye
        eye_x = head_x + 7 if not flip else head_x + 3
        pygame.draw.circle(surface, RAT_EYE_RED, (eye_x, sr.y + 5), 2)

        # Tail
        tail_x = sr.left if not flip else sr.right
        tail_dir = -1 if not flip else 1
        points = [
            (tail_x, sr.centery),
            (tail_x + tail_dir * 8, sr.y - 2),
            (tail_x + tail_dir * 14, sr.y - 6),
        ]
        pygame.draw.lines(surface, RAT_PINK, False, points, 2)

        # Whiskers
        wx = head_x + 9 if not flip else head_x
        wd = 1 if not flip else -1
        for dy in (-1, 1):
            pygame.draw.line(surface, RAT_WHISKER,
                             (wx, sr.y + 7),
                             (wx + wd * 8, sr.y + 5 + dy * 3), 1)
