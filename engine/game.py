import asyncio
import pygame
import sys
from settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS, TITLE,
    STATE_MENU, STATE_PLAYING, STATE_GAME_OVER, STATE_LEVEL_COMPLETE,
    NUM_LEVELS, STARTING_LIVES, EXTRA_LIFE_SCORE, MAX_LIVES
)
from engine.input_handler import InputHandler
from engine.camera import Camera
from world.level import Level
from world.background import Background
from ui.hud import HUD
from ui.menu import Menu


class Game:
    """Main game loop and state machine."""

    def __init__(self):
        pygame.init()
        pygame.mixer.init(22050, -16, 1, 512)
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.input = InputHandler()
        self.menu = Menu()
        self.hud = HUD()
        self.background = Background()

        self.state = STATE_MENU
        self.current_level_index = 0
        self.score = 0
        self.lives = STARTING_LIVES
        self.next_extra_life_score = EXTRA_LIFE_SCORE
        self.level = None

    def start_level(self, level_index):
        self.current_level_index = level_index
        self.level = Level(level_index, self)
        self.state = STATE_PLAYING

    def new_game(self):
        self.score = 0
        self.lives = STARTING_LIVES
        self.next_extra_life_score = EXTRA_LIFE_SCORE
        self.start_level(0)

    def add_score(self, points, x=0, y=0):
        self.score += points
        if x and y:
            self.hud.add_popup(f"+{points}", x, y)
        # Check for extra life
        while self.score >= self.next_extra_life_score and self.lives < MAX_LIVES:
            self.lives += 1
            self.next_extra_life_score += EXTRA_LIFE_SCORE
            self.hud.add_popup("1UP!", x, y - 30)

    def lose_life(self):
        self.lives -= 1
        if self.lives <= 0:
            self.state = STATE_GAME_OVER

    def complete_level(self):
        self.current_level_index += 1
        if self.current_level_index >= NUM_LEVELS:
            self.current_level_index = 0
            self.state = STATE_GAME_OVER  # Won the game
        else:
            self.state = STATE_LEVEL_COMPLETE

    async def run(self):
        running = True
        while running:
            dt = self.clock.tick(FPS) / 1000.0
            dt = min(dt, 0.05)  # Cap delta time

            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    running = False

            self.input.update(events)

            if self.input.escape_pressed:
                if self.state == STATE_PLAYING:
                    self.state = STATE_MENU
                elif self.state == STATE_MENU:
                    running = False

            if self.state == STATE_MENU:
                self._update_menu()
            elif self.state == STATE_PLAYING:
                self._update_playing(dt)
            elif self.state == STATE_GAME_OVER:
                self._update_game_over()
            elif self.state == STATE_LEVEL_COMPLETE:
                self._update_level_complete()

            pygame.display.flip()
            await asyncio.sleep(0)  # yield to browser event loop

        pygame.quit()

    def _update_menu(self):
        if self.input.enter_pressed:
            self.new_game()
        self.menu.draw_title(self.screen)
        self.input.touch.draw(self.screen, show_enter=True)

    def _update_playing(self, dt):
        self.level.update(dt, self.input)
        self.background.draw(self.screen, self.level.camera)
        self.level.draw(self.screen)
        self.hud.update(dt)
        self.hud.draw(self.screen, self.score, self.lives)
        self.input.touch.draw(self.screen, show_enter=False)

    def _update_game_over(self):
        if self.input.enter_pressed:
            self.state = STATE_MENU
        self.menu.draw_game_over(self.screen, self.score)
        self.input.touch.draw(self.screen, show_enter=True)

    def _update_level_complete(self):
        if self.input.enter_pressed:
            self.start_level(self.current_level_index)
        self.menu.draw_level_complete(self.screen, self.current_level_index, self.score)
        self.input.touch.draw(self.screen, show_enter=True)
