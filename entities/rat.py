import pygame
from settings import RAT_SPEED, TILE_SIZE, GRAVITY, MAX_FALL_SPEED, RAT_FLEE_SPEED, RAT_HIT_POINTS
from graphics.colors import RAT_GREY, RAT_DARK, RAT_PINK, RAT_EYE_RED, RAT_WHISKER
from engine.sounds import play as play_sound


class Rat:
    """Patrol enemy - walks back and forth on platforms."""

    WIDTH = 24
    HEIGHT = 16
    damage = True  # flag for player collision detection

    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, self.WIDTH, self.HEIGHT)
        self.speed = RAT_SPEED
        self.vel_y = 0
        self.on_ground = False
        self.facing_right = True
        self.alive = True
        self.walk_timer = 0
        self.fleeing = False
        self.flee_timer = 0

    def get_hit(self, direction):
        """Whacked by the hockey stick - squeak and run away."""
        if self.fleeing:
            return
        play_sound("squeak")
        self.fleeing = True
        self.flee_timer = 1.5
        # Run in opposite direction from the hit
        self.speed = -direction * RAT_FLEE_SPEED
        self.facing_right = self.speed > 0
        self.damage = False  # can't hurt player while fleeing

    def update(self, dt, tiles):
        if not self.alive:
            return

        # Fleeing countdown
        if self.fleeing:
            self.flee_timer -= dt
            if self.flee_timer <= 0:
                self.alive = False
                return

        self.walk_timer += dt * (12 if self.fleeing else 6)

        # Gravity
        self.vel_y += GRAVITY * dt
        if self.vel_y > MAX_FALL_SPEED:
            self.vel_y = MAX_FALL_SPEED

        # Apply vertical movement
        self.on_ground = False
        self.rect.y += int(self.vel_y * dt)
        for tile in tiles:
            if self.rect.colliderect(tile.rect):
                if self.vel_y > 0:
                    self.rect.bottom = tile.rect.top
                    self.vel_y = 0
                    self.on_ground = True
                elif self.vel_y < 0:
                    self.rect.top = tile.rect.bottom
                    self.vel_y = 0

        # Only patrol when on the ground
        if not self.on_ground:
            return

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

        # Fleeing rats don't care about edges - they run off
        if not self.fleeing:
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

        # Eye - wider when fleeing
        eye_x = head_x + 7 if not flip else head_x + 3
        eye_r = 3 if self.fleeing else 2
        pygame.draw.circle(surface, RAT_EYE_RED, (eye_x, sr.y + 5), eye_r)

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
