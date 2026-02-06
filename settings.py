# settings.py - All constants and tuning values

# Display
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
TITLE = "Silly Goose - Birmingham Streets"

# Tiles
TILE_SIZE = 40

# Player physics
PLAYER_SPEED = 200          # px/s
PLAYER_JUMP_VEL = -420      # px/s (negative = up)
GRAVITY = 980               # px/s^2
MAX_FALL_SPEED = 600        # px/s

# Player settings
STARTING_LIVES = 3
MAX_LIVES = 5
EXTRA_LIFE_SCORE = 1000
INVINCIBILITY_TIME = 2.0    # seconds after being hit

# Rat settings
RAT_SPEED = 80              # px/s

# Collectibles
BEER_POINTS = 50
CIDER_POINTS = 75
GOAL_POINTS = 200
BOB_SPEED = 2.0             # bobbing frequency
BOB_AMPLITUDE = 5           # bobbing pixels

# Hockey ball
BALL_HIT_SPEED = 350        # px/s
BALL_FRICTION = 0.97        # per-frame multiplier
BALL_GRAVITY = 400          # px/s^2
STICK_RANGE = 50            # pixels from player center

# Game states
STATE_MENU = "MENU"
STATE_PLAYING = "PLAYING"
STATE_GAME_OVER = "GAME_OVER"
STATE_LEVEL_COMPLETE = "LEVEL_COMPLETE"

# Levels
NUM_LEVELS = 3
