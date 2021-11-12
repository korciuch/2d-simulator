"""Constants used through the simulation."""

BOUNDS_WIDTH: int = 500
MAX_X: float = BOUNDS_WIDTH / 2
MIN_X: float = -MAX_X
VIEW_WIDTH: int = BOUNDS_WIDTH + 20

BOUNDS_HEIGHT: int = 500
MAX_Y: float = BOUNDS_HEIGHT / 2
MIN_Y: float = -MAX_Y
VIEW_HEIGHT: int = BOUNDS_HEIGHT + 20

NUM_ROWS: int = 10
NUM_COLS: int = 10

CELL_RADIUS: int = BOUNDS_HEIGHT / NUM_ROWS
CELL_COUNT: int = 25
CELL_SPEED: float = CELL_RADIUS
