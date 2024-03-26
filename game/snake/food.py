import pygame
import random


class Food:
    colour = (255, 0, 0)  # red
    square_size = None
    x_pos = None
    y_pos = None
    display_width = None
    display_height = None
    fruit = None
    display = None

    def __init__(self, display, grid_square_size, window_width, window_height):
        self.square_size = grid_square_size
        self.display = display
        self.display_width = window_width
        self.display_height = window_height
        self.random_movement()

    def generate_food(self):
        pygame.draw.rect(self.display, self.colour, self.fruit)

    def random_movement(self):
        grid_col_num = self.display_width / self.square_size
        grid_row_num = self.display_height / self.square_size
        self.x_pos = random.randint(0, grid_col_num - 1) * self.square_size
        self.y_pos = random.randint(0, grid_row_num - 1) * self.square_size
        self.fruit = pygame.Rect(self.x_pos, self.y_pos, self.square_size, self.square_size)
