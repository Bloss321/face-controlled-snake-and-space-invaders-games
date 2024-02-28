import pygame
import sys

from pygame import mixer

from game.space_invaders.alien import Alien
from game.space_invaders.laser import Laser
from game.space_invaders.player import Player

pygame.init()

display = pygame.display.set_mode((800, 600))

background = pygame.image.load('game/space_invaders/images/background.png')

pygame.display.set_caption("Space Invaders")
font = pygame.font.Font('freesansbold.ttf', 32)


def display_score(score: int):
    score = font.render("Score : " + str(score), True, (255, 255, 255))
    display.blit(score, (10, 10))


def display_game_over():
    game_over_font = pygame.font.Font('freesansbold.ttf', 64)
    over_text = game_over_font.render("GAME OVER", True, (255, 255, 255))
    display.blit(over_text, (200, 250))


# add sounds to game later

def run_game():
    player = Player()  # maybe make laser a player attribute?
    aliens = [Alien() for _ in range(6)]
    laser = Laser()
    score = 0

    clock = pygame.time.Clock()
    game_over = False

    while not game_over:
        display.fill((0, 0, 0))
        display.blit(background, (0, 0))

        # all this logic can go in separate function so that code can be used for CV game
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    player.x_change = -5
                if event.key == pygame.K_RIGHT:
                    player.x_change = 5
                if event.key == pygame.K_SPACE:
                    if laser.state == "inactive":
                        laser.x_pos = player.x_pos
                        laser.fire()
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                    player.x_change = 0

        player.move()
        laser.move()

        for alien in aliens:
            alien.move()
            has_collided = laser.has_collided_with_alien(alien)
            if has_collided:
                laser.regenerate()
                score += 1
                alien.__init__()

        if any(alien.y_pos > 440 for alien in aliens):
            display_game_over()
            break

        player.generate(display)
        laser.generate(display)
        for alien in aliens:
            alien.generate(display)
        display_score(score)
        pygame.display.update()
        clock.tick(60)


if __name__ == "__main__":
    run_game()
