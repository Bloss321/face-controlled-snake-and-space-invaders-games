import math

import pygame
from pygame import Rect

from game.space_invaders.alien import Alien
from game.space_invaders.player import Player


class Laser:
    def __init__(self):
        self.player_image = pygame.image.load('game/space_invaders/images/player_laser.png')
        self.alien_image = pygame.image.load('game/space_invaders/images/alien_laser.png')
        self.is_alien_laser = False  # when true the Laser object belongs to an alien, belongs to player by default
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

    # to move the alien's laser
    def move_alien_laser(self):
        # check if laser is out of bounds
        if self.y_pos >= 600:
            self.regenerate()
        if self.is_alien_laser:
            if self.state == "fire":
                self.y_pos += (self.y_jumps * 1.5)

    def generate(self, display):
        if self.state == "fire":
            if self.is_alien_laser:
                display.blit(self.alien_image, (self.x_pos + 16, self.y_pos - 10))
            else:
                display.blit(self.player_image, (self.x_pos + 16, self.y_pos + 10))

    def fire(self):
        self.state = "fire"

    # check if player's laser has collided with the alien
    def has_collided_with_alien(self, alien: Alien):
        # convert to rect objects to check for collisions
        alien_rect = alien.convert_to_rect()
        if alien_rect.colliderect(self.convert_to_rect()):
            return True
        else:
            return False

    # check if the alien's laser has collided with the player
    def has_collided_with_player(self, player: Player):
        player_rect = player.convert_to_rect()  # only a confirmed kill/collision if the player shield isn't activated
        if player_rect.colliderect(self.convert_to_rect()) and player.shield_activated is False:
            return True
        else:
            return False

    def regenerate(self):
        self.y_pos = 480
        self.state = "inactive"

    def convert_to_rect(self):
        rect = self.player_image.get_rect()
        rect.x = self.x_pos
        rect.y = self.y_pos
        return rect
