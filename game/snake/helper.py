from enum import Enum


class Direction(Enum):
    RIGHT = {"x": 1, "y": 0}
    LEFT = {"x": -1, "y": 0}
    UP = {"x": 0, "y": -1}
    DOWN = {"x": 0, "y": 1}
    NEUTRAL = {"x": 0, "y": 0}
