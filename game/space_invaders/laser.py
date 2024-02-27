import math

import pygame
from pygame import Rect

from game.space_invaders.alien import Alien


class Laser:
    def __init__(self):
        self.image = pygame.image.load('game/space_invaders/images/laser_beam.png')
        self.x_pos = 0
        self.y_pos = 480
        self.state = "inactive"
        self.y_jumps = 10  # change in y

    def move(self):
        # check if laser is out of bounds
        if self.y_pos <= 0:
            self.regenerate()
        if self.state == "fire":
            self.y_pos -= self.y_jumps

    def generate(self, display):
        if self.state == "fire":
            display.blit(self.image, (self.x_pos + 16, self.y_pos + 10))

    def fire(self):
        self.state = "fire"

    def has_collided(self, alien: Alien):
        # convert to rect objects to check for collisions
        alien_rect = alien.convert_to_rect()
        if alien_rect.colliderect(self.convert_to_rect()):
            return True
        else:
            return False

    def regenerate(self):
        self.y_pos = 480
        self.state = "inactive"

    def convert_to_rect(self):
        rect = self.image.get_rect()
        rect.x = self.x_pos
        rect.y = self.y_pos
        return rect
