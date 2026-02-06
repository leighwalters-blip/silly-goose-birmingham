import pygame


class InputHandler:
    """Keyboard input abstraction."""

    def __init__(self):
        self.left = False
        self.right = False
        self.jump_pressed = False
        self.hit_pressed = False
        self.enter_pressed = False
        self.escape_pressed = False

    def update(self, events):
        self.jump_pressed = False
        self.hit_pressed = False
        self.enter_pressed = False
        self.escape_pressed = False

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
