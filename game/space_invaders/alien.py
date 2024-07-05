import random

import pygame

from game.space_invaders.player import Player


class Alien:
    def __init__(self):
        images = [
            pygame.image.load('game/space_invaders/images/aliens/alien_1.png'),
            pygame.image.load('game/space_invaders/images/aliens/alien_2.png'),
            pygame.image.load('game/space_invaders/images/aliens/alien_3.png'),
            pygame.image.load('game/space_invaders/images/aliens/alien_4.png'),
            pygame.image.load('game/space_invaders/images/aliens/alien_5.png'),
            pygame.image.load('game/space_invaders/images/aliens/alien_6.png'),
        ]
        self.image = random.choice(images)
        self.x_pos = random.randint(0, 736)
        self.y_pos = random.randint(50, 150)
        self.x_change = 4
        self.y_change = 40

    def move(self):
        self.x_pos += self.x_change
        if self.x_pos <= 0:
            self.x_change = 4
            self.y_pos += self.y_change
        elif self.x_pos >= 736:
            self.x_change = -4
            self.y_pos += self.y_change

    # this doesn't actually make sense, have aliens shoot lasers instead
    def activate_random_drop(self, player: Player):
        if abs(self.x_pos - player.x_pos) < 80:
            self.random_drop = True
            self.perform_random_drop()

    def perform_random_drop(self):
        if self.random_drop:
            self.x_change = 0
            self.y_change = 80

    def generate(self, display):
        display.blit(self.image, (self.x_pos, self.y_pos))

    def convert_to_rect(self):
        rect = self.image.get_rect()
        rect.x = self.x_pos
        rect.y = self.y_pos
        return rect
