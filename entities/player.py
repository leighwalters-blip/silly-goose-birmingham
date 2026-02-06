import pygame
from settings import (
    PLAYER_SPEED, PLAYER_JUMP_VEL, GRAVITY, MAX_FALL_SPEED,
    TILE_SIZE, INVINCIBILITY_TIME, STICK_RANGE
)
from graphics.colors import (
    GOOSE_WHITE, GOOSE_BEAK_ORANGE, GOOSE_EYE_BLACK,
    GOOSE_EYE_WHITE, GOOSE_FEET_ORANGE, STICK_BROWN, STICK_DARK
)


class Player:
    """The silly goose."""

    WIDTH = 28
    HEIGHT = 36

    def __init__(self, x, y, game):
        self.game = game
        self.rect = pygame.Rect(x, y, self.WIDTH, self.HEIGHT)
        self.vel_x = 0
        self.vel_y = 0
        self.on_ground = False
        self.facing_right = True
        self.invincible_timer = 0
        self.hit_timer = 0  # brief animation when hitting

        # Animation
        self.walk_timer = 0
        self.walk_frame = 0

    def update(self, dt, input_handler, tiles, entities):
        # Horizontal movement
        self.vel_x = 0
        if input_handler.left:
            self.vel_x = -PLAYER_SPEED
            self.facing_right = False
        if input_handler.right:
            self.vel_x = PLAYER_SPEED
            self.facing_right = True

        # Jump
        if input_handler.jump_pressed and self.on_ground:
            self.vel_y = PLAYER_JUMP_VEL
            self.on_ground = False

        # Gravity
        self.vel_y += GRAVITY * dt
        if self.vel_y > MAX_FALL_SPEED:
            self.vel_y = MAX_FALL_SPEED

        # Hit / stick swing
        if input_handler.hit_pressed:
            self.hit_timer = 0.2
            self._check_ball_hit(entities)

        self.hit_timer = max(0, self.hit_timer - dt)
        self.invincible_timer = max(0, self.invincible_timer - dt)

        # Walk animation
        if self.vel_x != 0 and self.on_ground:
            self.walk_timer += dt * 8
            self.walk_frame = int(self.walk_timer) % 2
        else:
            self.walk_timer = 0
            self.walk_frame = 0

        # Move and collide
        self._move_axis(dt, tiles, 'x')
        self._move_axis(dt, tiles, 'y')

        # Check entity collisions
        self._check_entity_collisions(entities)

    def _move_axis(self, dt, tiles, axis):
        if axis == 'x':
            self.rect.x += int(self.vel_x * dt)
        else:
            self.rect.y += int(self.vel_y * dt)

        for tile in tiles:
            if not self.rect.colliderect(tile.rect):
                continue
            if axis == 'x':
                if self.vel_x > 0:
                    self.rect.right = tile.rect.left
                elif self.vel_x < 0:
                    self.rect.left = tile.rect.right
            else:
                if self.vel_y > 0:
                    self.rect.bottom = tile.rect.top
                    self.vel_y = 0
                    self.on_ground = True
                elif self.vel_y < 0:
                    self.rect.top = tile.rect.bottom
                    self.vel_y = 0

    def _check_ball_hit(self, entities):
        """Hit any hockey ball within stick range."""
        cx = self.rect.centerx
        cy = self.rect.centery
        direction = 1 if self.facing_right else -1
        for entity in entities:
            if hasattr(entity, 'get_hit'):
                dx = entity.rect.centerx - cx
                dy = entity.rect.centery - cy
                dist = (dx * dx + dy * dy) ** 0.5
                if dist < STICK_RANGE:
                    entity.get_hit(direction)

    def _check_entity_collisions(self, entities):
        for entity in entities:
            if not self.rect.colliderect(entity.rect):
                continue
            if hasattr(entity, 'collect'):
                entity.collect(self.game)
            elif hasattr(entity, 'damage') and self.invincible_timer <= 0:
                self.invincible_timer = INVINCIBILITY_TIME
                self.game.lose_life()
            elif hasattr(entity, 'reach_goal'):
                entity.reach_goal(self.game)

    def draw(self, surface, camera):
        # Blink when invincible
        if self.invincible_timer > 0 and int(self.invincible_timer * 10) % 2 == 0:
            return

        sr = camera.apply(self.rect)
        flip = not self.facing_right

        # Feet
        foot_y = sr.bottom - 4
        foot_offset = 4 if self.walk_frame == 0 else -2
        pygame.draw.ellipse(surface, GOOSE_FEET_ORANGE,
                            (sr.x + 4 + foot_offset, foot_y, 8, 5))
        pygame.draw.ellipse(surface, GOOSE_FEET_ORANGE,
                            (sr.x + 16 - foot_offset, foot_y, 8, 5))

        # Body
        body_rect = pygame.Rect(sr.x + 2, sr.y + 10, 24, 22)
        pygame.draw.ellipse(surface, GOOSE_WHITE, body_rect)

        # Neck
        neck_x = sr.x + 18 if not flip else sr.x + 4
        pygame.draw.ellipse(surface, GOOSE_WHITE,
                            (neck_x, sr.y + 2, 10, 18))

        # Head
        head_x = sr.x + 20 if not flip else sr.x + 2
        head_y = sr.y
        pygame.draw.circle(surface, GOOSE_WHITE, (head_x + 5, head_y + 6), 7)

        # Eye
        eye_x = head_x + 8 if not flip else head_x + 2
        pygame.draw.circle(surface, GOOSE_EYE_WHITE, (eye_x, head_y + 5), 3)
        pygame.draw.circle(surface, GOOSE_EYE_BLACK, (eye_x, head_y + 5), 1)

        # Beak
        if not flip:
            beak_pts = [(head_x + 12, head_y + 4), (head_x + 20, head_y + 7),
                        (head_x + 12, head_y + 9)]
        else:
            beak_pts = [(head_x - 2, head_y + 4), (head_x - 10, head_y + 7),
                        (head_x - 2, head_y + 9)]
        pygame.draw.polygon(surface, GOOSE_BEAK_ORANGE, beak_pts)

        # Hockey stick (when hitting)
        if self.hit_timer > 0:
            stick_x = sr.right + 2 if not flip else sr.left - 14
            pygame.draw.rect(surface, STICK_BROWN, (stick_x, sr.y + 8, 4, 28))
            pygame.draw.rect(surface, STICK_DARK, (stick_x - 2, sr.y + 32, 10, 4))
