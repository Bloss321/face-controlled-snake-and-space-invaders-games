import random

import pygame


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

    def generate(self, display):
        display.blit(self.image, (self.x_pos, self.y_pos))

    def convert_to_rect(self):
        rect = self.image.get_rect()
        rect.x = self.x_pos
        rect.y = self.y_pos
        return rect
