import pygame
from settings import TILE_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT
from engine.camera import Camera
from world.tile import Tile, EMPTY, GROUND, PLATFORM, BRICK, KERB
from entities.player import Player
from entities.rat import Rat
from entities.collectible import Collectible
from entities.hockey_ball import HockeyBall
from entities.goal import Goal


# Legend for level maps:
# . = empty    G = ground    P = platform    B = brick    K = kerb
# S = player start    R = rat    b = beer    c = cider
# H = hockey ball    X = goal

LEVEL_MAPS = [
    # Level 1 - The Digbeth Run
    [
        "........................................",
        "........................................",
        "........................................",
        "........................................",
        "........................................",
        "...........b....b..........c............",
        "..........PPP..PPP........PPP...........",
        "....b.........................b...c.....",
        "...PPP.............R.........PPPPPP.....",
        "...............b.......b................",
        "..............PPP.....PPP..........X....",
        ".....R...............................H..",
        "S...........R...............R...........",
        "GGKGGGGGGKGGGGGGGGKGGGGGGKGGGGGGGKGGGGG",
        "GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
    ],
    # Level 2 - Broad Street Bounce
    [
        "........................................",
        "........................................",
        "..................................c.....",
        ".................................PPP....",
        "........................................",
        "....c.........b.....b...................",
        "...PPP......PPP....PPP......PPP........",
        "........................................",
        "...........R..............R.....b..X....",
        "..b............................PPPPPP...",
        ".PPP...........b......c................",
        "..............PPP....PPP......H.........",
        ".....R...............R......R...........",
        "GGKGGGGGGKGGGGBBBGGKGGGGGGKGGGGGGGKGGGG",
        "GGGGGGGGGGGGGGBBBGGGGGGGGGGGGGGGGGGGGGG",
    ],
    # Level 3 - Bullring Blitz
    [
        "........................................",
        "........................................",
        ".......c................................",
        "......PPP.....c........................",
        "..............PPP...........c...........",
        "......................b....PPP..........",
        ".....b..............PPP.................",
        "....PPP......R.........................",
        ".............PPPP.........b.....X......",
        "..........................PPP..PPPP....",
        "..R...........R.....R..................",
        "......b.............H......H...........",
        "....PPP.........R........R.....R.......",
        "GGKGGGGKGGGGGGKGGGGBBKGGGGGGKGGGGGKGGGG",
        "GGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGGG",
    ],
]


class Level:
    """Loads and manages a single level."""

    def __init__(self, level_index, game):
        self.game = game
        self.tiles = []
        self.entities = []  # rats, collectibles, balls, goals
        self.player = None
        self.camera = None

        self._load(LEVEL_MAPS[level_index])

        level_w = len(LEVEL_MAPS[level_index][0]) * TILE_SIZE
        level_h = len(LEVEL_MAPS[level_index]) * TILE_SIZE
        self.camera = Camera(level_w, level_h)

    def _load(self, level_map):
        for gy, row in enumerate(level_map):
            for gx, char in enumerate(row):
                wx = gx * TILE_SIZE
                wy = gy * TILE_SIZE

                tile_type = {
                    'G': GROUND, 'P': PLATFORM, 'B': BRICK, 'K': KERB
                }.get(char)

                if tile_type is not None:
                    self.tiles.append(Tile(tile_type, gx, gy))

                elif char == 'S':
                    self.player = Player(wx, wy, self.game)
                elif char == 'R':
                    self.entities.append(Rat(wx, wy + TILE_SIZE - 16))
                elif char == 'b':
                    self.entities.append(Collectible(wx + 12, wy + 10, "beer"))
                elif char == 'c':
                    self.entities.append(Collectible(wx + 12, wy + 10, "cider"))
                elif char == 'H':
                    self.entities.append(HockeyBall(wx + TILE_SIZE // 2, wy + TILE_SIZE - 8))
                elif char == 'X':
                    self.entities.append(Goal(wx, wy - TILE_SIZE))

    def update(self, dt, input_handler):
        # Update player
        self.player.update(dt, input_handler, self.tiles, self.entities)

        # Update entities
        for entity in self.entities:
            if hasattr(entity, 'update'):
                if isinstance(entity, Rat):
                    entity.update(dt, self.tiles)
                elif isinstance(entity, HockeyBall):
                    entity.update(dt, self.tiles)
                else:
                    entity.update(dt)

        # Remove dead collectibles
        self.entities = [e for e in self.entities
                         if not (hasattr(e, 'alive') and not e.alive)]

        # Camera follows player
        self.camera.update(self.player.rect)

        # Fall death
        level_bottom = 15 * TILE_SIZE + 100
        if self.player.rect.top > level_bottom:
            self.game.lose_life()
            if self.game.lives > 0:
                self._respawn_player()

    def _respawn_player(self):
        """Put the player back at the start."""
        for gy, row in enumerate(LEVEL_MAPS[self.game.current_level_index]):
            for gx, char in enumerate(row):
                if char == 'S':
                    self.player.rect.x = gx * TILE_SIZE
                    self.player.rect.y = gy * TILE_SIZE
                    self.player.vel_x = 0
                    self.player.vel_y = 0
                    return

    def draw(self, surface):
        # Draw tiles
        for tile in self.tiles:
            tile.draw(surface, self.camera)

        # Draw entities
        for entity in self.entities:
            if hasattr(entity, 'draw'):
                entity.draw(surface, self.camera)

        # Draw player on top
        self.player.draw(surface, self.camera)
