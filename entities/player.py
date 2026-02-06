import math
import pygame
from settings import (
    PLAYER_SPEED, PLAYER_JUMP_VEL, GRAVITY, MAX_FALL_SPEED,
    TILE_SIZE, INVINCIBILITY_TIME, STICK_RANGE,
    RAT_HIT_POINTS, TRASH_CAN_POINTS
)
from graphics.colors import (
    GOOSE_WHITE, GOOSE_CREAM, GOOSE_BEAK_ORANGE, GOOSE_BEAK_TIP,
    GOOSE_EYE_BLACK, GOOSE_EYE_WHITE, GOOSE_EYE_RING,
    GOOSE_FEET_ORANGE, GOOSE_WING_GREY,
    STICK_BROWN, STICK_DARK
)
from entities.rat import Rat
from entities.trash_can import TrashCan


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
        self.drink_timer = 0  # drinking animation

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
            self._check_stick_hit(entities)

        self.hit_timer = max(0, self.hit_timer - dt)
        self.invincible_timer = max(0, self.invincible_timer - dt)
        self.drink_timer = max(0, self.drink_timer - dt)

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

    def _check_stick_hit(self, entities):
        """Hit any entity within stick range."""
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
                    # Award points for hitting rats and trash cans
                    if isinstance(entity, Rat) and not entity.fleeing:
                        self.game.add_score(RAT_HIT_POINTS,
                                            entity.rect.centerx, entity.rect.y)
                    elif isinstance(entity, TrashCan) and not entity.destroying:
                        self.game.add_score(TRASH_CAN_POINTS,
                                            entity.rect.centerx, entity.rect.y)

    def _check_entity_collisions(self, entities):
        for entity in entities:
            if not self.rect.colliderect(entity.rect):
                continue
            if hasattr(entity, 'collect') and entity.alive:
                entity.collect(self.game)
                self.drink_timer = 0.5  # trigger drinking animation
            elif hasattr(entity, 'damage') and entity.damage and self.invincible_timer <= 0:
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
        drinking = self.drink_timer > 0

        # Feet with webbed toes
        foot_y = sr.bottom - 4
        foot_offset = 4 if self.walk_frame == 0 else -2
        for fx, fo in [(sr.x + 4 + foot_offset, 0), (sr.x + 16 - foot_offset, 0)]:
            pygame.draw.ellipse(surface, GOOSE_FEET_ORANGE, (fx, foot_y, 10, 5))
            # Webbed toe lines
            pygame.draw.line(surface, (200, 120, 0), (fx + 2, foot_y + 1), (fx, foot_y + 4), 1)
            pygame.draw.line(surface, (200, 120, 0), (fx + 5, foot_y + 1), (fx + 5, foot_y + 4), 1)
            pygame.draw.line(surface, (200, 120, 0), (fx + 8, foot_y + 1), (fx + 10, foot_y + 4), 1)

        # Tail feathers (behind body)
        tail_x = sr.x - 2 if not flip else sr.right - 4
        tail_dir = -1 if not flip else 1
        for i in range(3):
            ty = sr.y + 18 + i * 3
            pygame.draw.line(surface, GOOSE_CREAM,
                             (tail_x + 6, ty),
                             (tail_x + tail_dir * 8, ty - 2 + i), 2)

        # Body
        body_rect = pygame.Rect(sr.x + 2, sr.y + 10, 24, 22)
        pygame.draw.ellipse(surface, GOOSE_WHITE, body_rect)

        # Wing detail on body
        wing_x = sr.x + 6 if not flip else sr.x + 10
        wing_rect = pygame.Rect(wing_x, sr.y + 14, 14, 14)
        pygame.draw.ellipse(surface, GOOSE_WING_GREY, wing_rect)
        # Wing feather lines
        for i in range(3):
            wy = sr.y + 17 + i * 4
            pygame.draw.line(surface, GOOSE_CREAM,
                             (wing_x + 2, wy), (wing_x + 12, wy), 1)

        if drinking:
            # Drinking pose: neck straight up, head tilted back
            neck_x = sr.centerx - 5
            pygame.draw.ellipse(surface, GOOSE_WHITE,
                                (neck_x, sr.y - 8, 10, 22))
            # Head tilted back
            head_cx = sr.centerx
            head_cy = sr.y - 12
            pygame.draw.circle(surface, GOOSE_WHITE, (head_cx, head_cy), 7)
            # Eye (looking up)
            self._draw_eye(surface, head_cx + 2, head_cy - 3)
            # Beak pointing up
            beak_pts = [(head_cx - 3, head_cy - 7), (head_cx, head_cy - 16),
                        (head_cx + 3, head_cy - 7)]
            pygame.draw.polygon(surface, GOOSE_BEAK_ORANGE, beak_pts)
            pygame.draw.polygon(surface, GOOSE_BEAK_TIP, beak_pts, 1)
        else:
            # Normal pose
            # Neck
            neck_x = sr.x + 18 if not flip else sr.x + 4
            pygame.draw.ellipse(surface, GOOSE_WHITE,
                                (neck_x, sr.y + 2, 10, 18))

            # Head
            head_x = sr.x + 20 if not flip else sr.x + 2
            head_y = sr.y
            pygame.draw.circle(surface, GOOSE_WHITE, (head_x + 5, head_y + 6), 8)

            # Eye with proper goose detail
            eye_x = head_x + 8 if not flip else head_x + 2
            eye_y = head_y + 5
            self._draw_eye(surface, eye_x, eye_y)

            # Beak - proper goose beak shape with nostril and dark tip
            if not flip:
                # Upper beak
                beak_pts = [(head_x + 10, head_y + 3), (head_x + 22, head_y + 6),
                            (head_x + 10, head_y + 7)]
                pygame.draw.polygon(surface, GOOSE_BEAK_ORANGE, beak_pts)
                # Lower beak
                lower_pts = [(head_x + 10, head_y + 7), (head_x + 20, head_y + 7),
                             (head_x + 10, head_y + 9)]
                pygame.draw.polygon(surface, GOOSE_BEAK_ORANGE, lower_pts)
                # Dark tip / nail on beak
                pygame.draw.circle(surface, GOOSE_BEAK_TIP, (head_x + 21, head_y + 6), 2)
                # Nostril
                pygame.draw.circle(surface, GOOSE_BEAK_TIP, (head_x + 15, head_y + 5), 1)
                # Mouth line
                pygame.draw.line(surface, GOOSE_BEAK_TIP,
                                 (head_x + 10, head_y + 7), (head_x + 20, head_y + 7), 1)
            else:
                beak_pts = [(head_x + 2, head_y + 3), (head_x - 10, head_y + 6),
                            (head_x + 2, head_y + 7)]
                pygame.draw.polygon(surface, GOOSE_BEAK_ORANGE, beak_pts)
                lower_pts = [(head_x + 2, head_y + 7), (head_x - 8, head_y + 7),
                             (head_x + 2, head_y + 9)]
                pygame.draw.polygon(surface, GOOSE_BEAK_ORANGE, lower_pts)
                pygame.draw.circle(surface, GOOSE_BEAK_TIP, (head_x - 9, head_y + 6), 2)
                pygame.draw.circle(surface, GOOSE_BEAK_TIP, (head_x - 3, head_y + 5), 1)
                pygame.draw.line(surface, GOOSE_BEAK_TIP,
                                 (head_x + 2, head_y + 7), (head_x - 8, head_y + 7), 1)

        # Hockey stick (always visible, swings forward when hitting)
        self._draw_stick(surface, sr, flip)

    def _draw_eye(self, surface, x, y):
        """Draw a detailed goose eye with ring and pupil."""
        # Eye ring (dark skin patch around eye, like real geese)
        pygame.draw.circle(surface, GOOSE_EYE_RING, (x, y), 4, 1)
        # White of eye
        pygame.draw.circle(surface, GOOSE_EYE_WHITE, (x, y), 3)
        # Iris (dark brown/black)
        pygame.draw.circle(surface, (50, 40, 30), (x, y), 2)
        # Pupil
        pygame.draw.circle(surface, GOOSE_EYE_BLACK, (x, y), 1)
        # Tiny highlight
        pygame.draw.circle(surface, GOOSE_EYE_WHITE, (x + 1, y - 1), 1)

    def _draw_stick(self, surface, sr, flip):
        """Draw a hockey stick with curved blade, always visible."""
        swinging = self.hit_timer > 0
        if swinging:
            swing_progress = 1.0 - (self.hit_timer / 0.2)
            angle = -30 + swing_progress * 90
        else:
            angle = -20

        if flip:
            angle = -angle

        # Stick grip point
        grip_x = sr.centerx + (4 if not flip else -4)
        grip_y = sr.y + 16

        # Shaft
        shaft_len = 30
        rad = math.radians(angle)
        end_x = grip_x + shaft_len * math.sin(rad) * (1 if not flip else -1)
        end_y = grip_y + shaft_len * math.cos(rad)

        # Draw shaft
        pygame.draw.line(surface, STICK_BROWN,
                         (int(grip_x), int(grip_y)),
                         (int(end_x), int(end_y)), 3)

        # Curved blade
        blade_dir = 1 if not flip else -1
        blade_len = 12
        blade_end_x = end_x + blade_dir * blade_len * math.cos(math.radians(angle))
        blade_end_y = end_y + blade_len * 0.3

        mid_x = (end_x + blade_end_x) / 2 + blade_dir * 3
        mid_y = (end_y + blade_end_y) / 2 + 2
        points = [
            (int(end_x), int(end_y)),
            (int(mid_x), int(mid_y)),
            (int(blade_end_x), int(blade_end_y))
        ]
        pygame.draw.lines(surface, STICK_DARK, False, points, 4)
