import pygame

from game.snake.food import Food
from game.snake.helper import Direction


class Snake:
    colour = (0, 255, 0)  # green
    square_size = None  # game grid square size
    direction = Direction.RIGHT
    x_pos = None
    y_pos = None
    length = None
    body = None
    display_width = None
    display_height = None
    has_eaten_itself = False
    is_out_of_bounds = False

    def __init__(self, grid_square_size, window_width, window_height):
        self.square_size = grid_square_size
        self.x_pos = self.square_size * 4  # snake starts in middle of grid
        self.y_pos = self.square_size * 6
        self.display_width = window_width
        self.display_height = window_height
        self.body = [pygame.Rect(self.x_pos - self.square_size, self.y_pos, self.square_size, grid_square_size)]
        self.length = 2

    def generate_snake_body(self, display):
        for square in self.body:
            pygame.draw.rect(display, self.colour, square)

    def set_position(self, current_head, direction):
        next_head = pygame.Rect(current_head.x + (direction["x"] * self.square_size),
                                current_head.y + (direction["y"] * self.square_size),
                                self.square_size, self.square_size)
        self.body.append(next_head)

    def move_snake(self):
        head = self.body[-1]
        self.set_position(head, self.direction.value)
        if self.length < len(self.body):
            self.body.pop(0)
        self.check_collisions()

    def eat_food(self, food: Food):
        head = self.body[-1]
        if head.x == food.x_pos and head.y == food.y_pos:
            self.set_position(head, self.direction.value)
            self.length += 1
            food.random_movement()
            food.generate_food()

    def check_collisions(self):
        head = self.body[-1]
        body = self.body.copy()
        body.pop()
        if head in body:
            self.has_eaten_itself = True
        if head.x not in range(0, self.display_width) or head.y not in range(0, self.display_height):
            self.is_out_of_bounds = True
