import pygame

from game.snake.common.helper import Direction


class Laser2:
    colour = (255, 0, 255)
    length = None
    thickness = None
    x_pos = None
    y_pos = None
    snake_direction = None
    direction = Direction.NEUTRAL
    out_of_bounds = False
    collision = False  # may not need this
    success = False
    used_up = False  # if used up - the laser beam ceases to exist
    state = "inactive"  # state can be active/inactive
    movement_count = 0

    square_size = None
    display_height = None
    display_width = None

    def __init__(self, grid_square_size, window_height, window_width):
        self.square_size = grid_square_size
        self.display_height = window_height
        self.display_width = window_width
        # self.snake_direction = snake_dir
        self.thickness = self.square_size * 0.2
        self.length = self.square_size
        pass

    def generate_laser(self, display, snake_direction, snake_x, snake_y):
        if self.movement_count == 0:
            self.direction = snake_direction
            self.x_pos = snake_x
            self.y_pos = snake_y
        self.x_pos = self.x_pos + (self.direction.value.get('x') * (self.square_size * self.movement_count))
        self.y_pos = self.y_pos + (self.direction.value.get('y') * (self.square_size * self.movement_count))

        laser = pygame.Rect(self.x_pos, self.y_pos, self.thickness, self.length)
        if self.direction == Direction.LEFT or self.direction == Direction.RIGHT:
            laser = pygame.Rect(self.x_pos, self.y_pos, self.length, self.thickness)
        pygame.draw.rect(display, self.colour, laser)

        self.movement_count = self.movement_count + 1
        laser_pos = (self.x_pos, self.y_pos)
        return laser_pos

    def move_laser(self, count):
        self.x_pos = self.x_pos + (self.direction.value.get('x') * (self.square_size * count))
        self.y_pos = self.y_pos + (self.direction.value.get('y') * (self.square_size * count))

    def check_out_of_bounds(self):
        if self.x_pos not in range(0, self.display_width) or self.y_pos not in range(0, self.display_height):
            self.out_of_bounds = True
