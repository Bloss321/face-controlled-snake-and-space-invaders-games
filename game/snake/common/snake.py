import pygame
from pygame import Rect

from game.snake.advanced.Laser_2 import Laser2
from game.snake.common.food import Food
from game.snake.common.helper import Direction


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

    laser_direction = Direction.NEUTRAL  # will remove!
    laser_x = None
    laser_y = None

    # for the advanced game
    # release_laser = False  # back to false after laser_collision is true  - removing
    laser_collision = False  # laser has collided with the bad fruit
    laser_state = "inactive"  # active/inactive or active (maybe should be enum)
    laser_out_of_bounds = False
    lasers: list[Laser2] = []  # do I need?

    def __init__(self, grid_square_size, window_width, window_height):
        self.square_size = grid_square_size
        self.x_pos = self.square_size
        self.y_pos = self.square_size
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
        for snake_square in body:
            if head.x == snake_square.x and head.y == snake_square.y:
                self.has_eaten_itself = True
            if head.x not in range(0, self.display_width) or head.y not in range(0, self.display_height):
                self.is_out_of_bounds = True

    #  for the advanced game

    # this method only works on first iteration? Laser stops after 1 block
    def fire_laser_simple(self, display, count):
        # laser initially starts with no direction, as the first call:  laser direction =  snake direction
        # laser_x = last_laser_pos[0] + (self.laser_direction.value.get('x') * (self.square_size * count))
        # laser_y = last_laser_pos[1] + (self.laser_direction.value.get('y') * (self.square_size * count))

        if count == 1:
            self.laser_direction = self.direction
            snake_head = self.body[-1]
            self.laser_x = snake_head.x
            self.laser_y = snake_head.y

        # the laser direction should always stay the same, until a new one is called
        # need to be able to shoot multiple lasers

        # snake_head = self.body[-1]
        self.laser_x = self.laser_x + (self.laser_direction.value.get('x') * (self.square_size * count))
        self.laser_y = self.laser_y + (self.laser_direction.value.get('y') * (self.square_size * count))
        thickness = self.square_size * 0.2
        laser_length = self.square_size
        laser_colour = (255, 0, 255)

        laser = pygame.Rect(self.laser_x, self.laser_y, thickness, laser_length)
        if self.laser_direction == Direction.LEFT or self.laser_direction == Direction.RIGHT:
            laser = pygame.Rect(self.laser_x, self.laser_y, laser_length, thickness)

        pygame.draw.rect(display, laser_colour, laser)

        laser_pos = (self.laser_x, self.laser_y)
        return laser_pos

    def check_laser_out_of_bounds(self, laser_x, laser_y):
        if laser_x not in range(0, self.display_width) or laser_y not in range(0, self.display_height):
            self.laser_out_of_bounds = True

    '''

    def fire_laser(self, laser: Laser):
        # self.check_laser_out_of_bounds(laser)
        if laser.released:
            # makes no sense - should be while loop in game file
            if not self.laser_collision and not self.is_out_of_bounds:
                laser.generate_laser()
            else:
                laser.released = False

    # if the laser has collided with the bad snake, delete the snake from the list of snakes & generate 2 more
    # need to consider this logic more closely
    def laser_collided(self, laser: Laser, bad_foods: list[Rect], direction: Direction):  # takes in bad_food.fruits
        # if the direction is up or down - take fruit with matching x coord as snake
        # of thew direction is left/right - take fruit with matching y coord
        laser_food_x = laser.x_pos
        laser_food_y = laser.y_pos

        if direction == Direction.UP or direction == Direction.DOWN:
            bad_foods_in_scope = filter(lambda fruit: fruit.x == self.x_pos, bad_foods)

            for food in bad_foods_in_scope:
                if direction == Direction.UP:
                    laser_food_x = laser.x_pos - (0.4 * self.square_size)
                    laser_food_y = laser.y_pos - self.square_size
                elif direction == Direction.DOWN:
                    laser_food_x = laser.x_pos - (0.4 * self.square_size)
                    laser_food_y = laser.y_pos + (1.5 * self.square_size)

                if laser_food_x == food.x and laser_food_y == food.y:
                    self.laser_collision = True
                    laser.released = False
                else:
                    self.laser_collision = False

        elif direction == Direction.LEFT or direction == Direction.RIGHT:
            bad_foods_in_scope = filter(lambda fruit: fruit.y == self.y_pos, bad_foods)

            for food in bad_foods_in_scope:
                if direction == Direction.RIGHT:
                    laser_food_x = laser.x_pos + (1.5 * self.square_size)
                    laser_food_y = laser.y_pos - (0.4 * self.square_size)

                elif direction == Direction.LEFT:
                    laser_food_x = laser.x_pos - self.square_size
                    laser_food_y = laser.y_pos - (0.4 * self.square_size)

                if laser_food_x == food.x and laser_food_y == food.y:
                    self.laser_collision = True
                    laser.released = False
                else:
                    self.laser_collision = False
                    
    '''
