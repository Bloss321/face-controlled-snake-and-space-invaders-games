import pygame
import time

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


shield_timer_running = False
start_shield_time = 0


def start_shield_timer():
    global shield_timer_running, start_shield_time
    shield_timer_running = True
    start_shield_time = time.time()


def stop_shield_timer():
    global shield_timer_running
    shield_timer_running = False
    pass


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

        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT] and keys[pygame.K_LSHIFT]:
            player.x_change = -10  # dash function when player holds shift & left/right direction
        elif keys[pygame.K_LEFT]:
            player.x_change = -4
        elif keys[pygame.K_RIGHT] and keys[pygame.K_LSHIFT]:
            player.x_change = 10
        elif keys[pygame.K_RIGHT]:
            player.x_change = 4
        else:
            player.x_change = 0

        if keys[pygame.K_SPACE]:
            if laser.state == "inactive":
                laser.x_pos = player.x_pos
                laser.fire()

        if keys[pygame.K_s] and player.shield_activated is False:
            player.shield_activation_num += 1
            if player.shield_activation_num > player.max_shield_activations:
                max_shield_activations_text = font.render("Max Shield Activations Reached", True, (255, 255, 255))
                display.blit(max_shield_activations_text, (350, 250))
            else:
                player.shield_activated = True
                player.is_shield_activated()
                start_shield_timer()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True

        player.move()
        laser.move()

        if shield_timer_running:  # while the shield is activated
            elapsed_shield_time = time.time() - start_shield_time

            # shield is activated for 3 seconds
            if elapsed_shield_time >= 3:
                stop_shield_timer()
                player.shield_activated = False
                player.is_shield_activated()

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
