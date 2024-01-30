from pygame import Rect
from game.snake.advanced.bad_snake import BadSnake


class BadSnakes:
    num_of_snakes = 3
    snakes: list[BadSnake] = []
    square_size = None
    display_width = None
    display_height = None
    score = 0
    snakes_killed = 0

    def __init__(self, grid_square_size, window_width, window_height):
        self.square_size = grid_square_size
        self.display_width = window_width
        self.display_height = window_height
        self.create_random_snakes(self.num_of_snakes, 1)  # initially the snake length is 1

    def create_random_snakes(self, num_of_snakes, snake_length):
        for i in range(num_of_snakes):
            # append new BadSnake with random values
            if len(self.snakes) <= 3:
                self.snakes.append(BadSnake(self.square_size, self.display_width, self.display_height, snake_length))

    def generate_snakes(self, display):
        for snake in self.snakes:
            snake.generate_snake_body(display)

    def move_snakes(self):
        for snake in self.snakes:
            snake.move_snake()

    def hit_player_snake(self, player_snake_body: list[Rect]):
        for snake in self.snakes:
            snake.hit_good_snake(player_snake_body)
            if snake.hit_player_snake:
                self.score += 1
                snake.hit_player_snake = False

    def generate_new_snakes(self, snake_len):
        for i in range(len(self.snakes)):
            snake = self.snakes[i]
            snake.check_if_out_of_bounds()
            if snake.is_out_of_bounds or snake.laser_hit:
                if snake_len < 10:
                    snake_len += 1
                self.snakes[i] = BadSnake(self.square_size, self.display_width, self.display_height, snake_len)
        return snake_len  # to store the length of the snake body

    def check_laser_hits(self, laser_x, laser_y):
        laser_success = False
        for snake in self.snakes:
            snake.is_killed(laser_x, laser_y)
            if snake.laser_hit:
                self.snakes_killed += 1
                laser_success = True
        return laser_success
