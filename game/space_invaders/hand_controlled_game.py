import pygame
import time
import random

from pygame import mixer

from game.countdown.game_countdown import start_game_countdown
from game.space_invaders.alien import Alien
from game.space_invaders.laser import Laser
from game.space_invaders.player import Player

pygame.init()
display_width = 800
display_height = 600
display = pygame.display.set_mode((800, 600))

background = pygame.image.load('game/space_invaders/images/background.png')

pygame.display.set_caption("Space Invaders")
font = pygame.font.Font('freesansbold.ttf', 32)


def display_score(score: int):
    score = font.render("Score : " + str(score), True, (255, 255, 255))
    display.blit(score, (10, 10))


def display_timer(timer: int):
    white = (255, 255, 255)
    cooper_font = pygame.font.SysFont("Cooper", 50)
    text = cooper_font.render(str(timer), True, white)
    display.blit(text, (400, 10))


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

def run_game(start, result_metrics, file_name):
    player = Player()  # maybe make laser a player attribute?
    aliens = [Alien() for _ in range(6)]
    laser = Laser()
    alien_laser = Laser()
    alien_laser.is_alien_laser = True
    score = 0
    hits_from_invaders = 0

    counter = 0

    clock = pygame.time.Clock()
    game_over = False
    failed_game = False

    while not game_over:
        # start 3-second countdown at beginning of game
        if counter == 0:
            start_game_countdown(display, 800, 600)
            print("Countdown Finished.")

        counter += 1
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
        alien_laser.move_alien_laser()

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

        if counter % 100 == 0:
            alien = random.choice(aliens)
            if alien_laser.state == "inactive":
                alien_laser.x_pos = alien.x_pos
                alien_laser.y_pos = alien.y_pos
                alien_laser.fire()

        # check if the alien's laser has collided with a player
        has_collided_with_player = alien_laser.has_collided_with_player(player)
        if has_collided_with_player:
            hits_from_invaders += 1  # player's score decreases by 1 each time they are hit by the alien

        # if the alien gets to the bottom of the screen, game over
        player_top_y_pos = display_height - player.image.get_height()
        if any(alien.y_pos > 440 for alien in aliens):
            print("Player Y Position" + str(player_top_y_pos))
            # display_game_over()
            failed_game = True  # I'm not using this?
            result_metrics["number_of_game_failures"] += 1
            result_metrics["scores_per_game"] += [score]
            result_metrics["hits_from_invaders_per_game"] += [hits_from_invaders]

        start_fail_timer = time.time()
        while failed_game:
            yellow = (255, 255, 0)
            font2 = pygame.font.Font('freesansbold.ttf', 25)
            message = font2.render("Game Over! The Space Invaders have reached you!", True, yellow)
            if time.time() - start_fail_timer < 3:
                display.blit(message, (display_width / 7, display_height / 20))
                pygame.display.update()
            else:
                failed_game = False

                if time.time() - start > 90:
                    break
                else:
                    continue

            # reset game stats so player starts from 0
            player = Player()  # maybe make laser a player attribute?
            aliens = [Alien() for _ in range(6)]
            laser = Laser()
            alien_laser = Laser()
            alien_laser.is_alien_laser = True
            score = 0
            hits_from_invaders = 0

        # generate sprites
        player.generate(display)
        laser.generate(display)
        alien_laser.generate(display)
        for alien in aliens:
            alien.generate(display)

        display_score(score)
        display_timer(90 - int(time.time() - start))

        if time.time() - start > 90:
            game_over = True
            result_metrics["scores_per_game"] += [score]
            result_metrics["hits_from_invaders_per_game"] += [hits_from_invaders]

        pygame.display.update()
        clock.tick(60)

    print("Keyboard-Controlled Space Invaders")
    print(result_metrics)
    f = open(file_name, "a")
    f.write("\nKeyboard-controlled Space Invaders metrics " + str(result_metrics))
    f.close()
