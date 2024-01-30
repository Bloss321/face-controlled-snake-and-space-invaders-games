from pygame import Rect

from game.snake.common.helper import Direction
from game.snake.common.snake import Snake
import random
import pygame


def random_colour():
    colours = [
        (0, 0, 255),  # blue
        (255, 255, 0),  # yellow
        (0, 128, 128),  # teal
        (255, 69, 0),  # orange
        (186, 85, 211),  # purple
        (135, 206, 250)  # light blue
    ]
    random_index = random.randrange(len(colours))
    return colours[random_index]


class BadSnake(Snake):
    hit_player_snake = False
    killed = False  # don't think I'm using this?
    laser_hit = False

    def __init__(self, grid_square_size, window_width, window_height, snake_length):
        Snake.__init__(self, grid_square_size, window_width, window_height)
        start_pos = self.random_start_pos()
        self.x_pos = start_pos[0]
        self.y_pos = start_pos[1]
        self.direction = self.get_direction_from_pos(self.x_pos, self.y_pos)
        self.colour = random_colour()
        self.body = [pygame.Rect(self.x_pos, self.y_pos, self.square_size, grid_square_size)]
        self.length = snake_length  # may take another look at this and increase to 2

    def random_start_pos(self):
        positions: list[tuple[int, int]] = []  # all possible game positions
        # number of rows in the game grid
        grid_row_num = int(self.display_height / self.square_size)  # 24
        grid_col_num = int(self.display_width / self.square_size)  # 24

        for x in range(grid_col_num):  # 0 to 23
            for y in range(grid_row_num):
                x_pos = x * self.square_size
                y_pos = y * self.square_size

                if x_pos == 0 or x_pos == (self.display_width - self.square_size):
                    positions.append((x_pos, y_pos))
                else:
                    if y_pos == 0 or y_pos == (self.display_height - self.square_size):
                        positions.append((x_pos, y_pos))

        random_index = random.randrange(len(positions))
        # choose a random position from array for bad snake
        return positions[random_index]

    # don't need generate_snake_body

    # can reformat this method and make it more compact
    def get_direction_from_pos(self, x_pos, y_pos):
        if x_pos == 0 and self.square_size <= y_pos < (self.display_height - self.square_size):
            return Direction.RIGHT
        elif x_pos == (self.display_width - self.square_size) and \
                self.square_size <= y_pos < (self.display_height - self.square_size):
            return Direction.LEFT
        elif y_pos == 0 and self.square_size <= x_pos < (self.display_width - self.square_size):
            return Direction.DOWN
        else:
            return Direction.UP

    def hit_good_snake(self, player_snake_body: list[Rect]):
        # if any part of the bad snake touches any part of the good snake
        break_out = False  # flag to break out of nested loop
        for square in player_snake_body:  # if it hits the snake once in the head I think - WILL CHANGE!
            for bad_square in self.body:
                if square.x == bad_square.x and square.y == bad_square.y:
                    head = self.body[-1]
                    self.hit_player_snake = True
                    self.set_position(head, self.direction.value)
                    break_out = True
                    break
            if break_out:
                break
            # else:
                # continue  # not working as it should???
            # break

    '''
    def hit_good_snake(self, player_snake_body: list[Rect]):
        # if any part of the bad snake touches any part of the good snake
        for bad_square in self.body:  # for square in the good snake - swap around 
            for square in player_snake_body:
                if bad_square.x == square.x and bad_square.y == square.y:
                    head = self.body[-1]
                    self.hit_player_snake = True
                    self.set_position(head, self.direction.value)
                    # self.length += 1
    '''

    def check_if_out_of_bounds(self):
        tail = self.body[0]  # instead of self.body[-1], why???
        if tail.x not in range(0, self.display_width) or tail.y not in range(0, self.display_height):
            self.is_out_of_bounds = True

    # if the snake is killed by the laser - remove it and generate new ones
    def is_killed(self, laser_x, laser_y):
        for square in self.body:
            if laser_x == square.x and laser_y == square.y:
                self.laser_hit = True
