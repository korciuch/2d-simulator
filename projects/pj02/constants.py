"""Constants used through the simulation."""

BOUNDS_WIDTH: int = 550
MAX_X: float = BOUNDS_WIDTH / 2
MIN_X: float = -MAX_X
VIEW_WIDTH: int = BOUNDS_WIDTH + 20

BOUNDS_HEIGHT: int = 550
MAX_Y: float = BOUNDS_HEIGHT / 2
MIN_Y: float = -MAX_Y
VIEW_HEIGHT: int = BOUNDS_HEIGHT + 20

NUM_ROWS: int = 25
NUM_COLS: int = 25

CELL_RADIUS: int = BOUNDS_HEIGHT / NUM_ROWS
CELL_COUNT: int = 10
CELL_SPEED: float = CELL_RADIUS

END_STATE = (0,NUM_COLS-1)
LOSS_REWARD: int = -50000