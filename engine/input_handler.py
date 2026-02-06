import pygame
from engine.touch_controls import TouchControls


class InputHandler:
    """Keyboard + touch input abstraction."""

    def __init__(self):
        self.left = False
        self.right = False
        self.jump_pressed = False
        self.hit_pressed = False
        self.enter_pressed = False
        self.escape_pressed = False
        self.touch = TouchControls()

    def update(self, events):
        self.jump_pressed = False
        self.hit_pressed = False
        self.enter_pressed = False
        self.escape_pressed = False

        # Keyboard input
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.jump_pressed = True
                if event.key == pygame.K_x or event.key == pygame.K_z:
                    self.hit_pressed = True
                if event.key == pygame.K_RETURN:
                    self.enter_pressed = True
                if event.key == pygame.K_ESCAPE:
                    self.escape_pressed = True

        keys = pygame.key.get_pressed()
        self.left = keys[pygame.K_LEFT] or keys[pygame.K_a]
        self.right = keys[pygame.K_RIGHT] or keys[pygame.K_d]

        # Touch input (merged with keyboard)
        self.touch.update(events)
        if "left" in self.touch.pressed:
            self.left = True
        if "right" in self.touch.pressed:
            self.right = True
        if "jump" in self.touch.just_pressed:
            self.jump_pressed = True
        if "hit" in self.touch.just_pressed:
            self.hit_pressed = True
        if "enter" in self.touch.just_pressed:
            self.enter_pressed = True
