import pygame


class Player:
    image = None

    def __init__(self):
        # self.image = pygame.image.load('game/space_invaders/player.png')
        # self.image_shield_activated = pygame.image.load('game/space_invaders/shield_activated.png')
        self.x_pos = 370
        self.y_pos = 480
        self.x_change = 0
        # shield activation power-up logic
        self.shield_activated = False  # for when the player's shield is activated
        self.is_shield_activated()  # to set the correct player image
        self.shield_activation_num = 0
        self.max_shield_activations = 3

    def move(self):
        self.x_pos += self.x_change
        if self.x_pos <= 0:
            self.x_pos = 0
        elif self.x_pos > 736:
            self.x_pos = 736

    def is_shield_activated(self):
        if self.shield_activated:
            self.image = pygame.image.load('game/space_invaders/images/shield_activated.png')
        else:
            self.image = pygame.image.load('game/space_invaders/images/player.png')

    def generate(self, display):
        display.blit(self.image, (self.x_pos, self.y_pos))
