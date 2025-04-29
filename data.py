from enum import Enum

class Color(Enum):
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)

class Facing(Enum):
    NORTH = 1
    SOUTH = 2
    EAST  = 3
    WEST  = 4