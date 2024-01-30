import sys
import pygame
import time

from game.snake.advanced.Laser_2 import Laser2
from game.snake.advanced.bad_snakes import BadSnakes
from game.snake.common.helper import Direction
from game.snake.common.snake import Snake
from game.snake.common.food import Food

pygame.init()

display_width = 600
display_height = 600
grid_square_size: int = 25

font = pygame.font.SysFont("Comic Sans", grid_square_size)
font2 = pygame.font.SysFont("Comic Sans", int(grid_square_size / 1.5))

display = pygame.display.set_mode((display_width, display_height))
pygame.display.set_caption('Head-controlled Snake Game')

clock = pygame.time.Clock()
snake_speed = 5  # 5


def create_game_grid():
    for row in range(0, display_width, grid_square_size):
        for col in range(0, display_height, grid_square_size):
            rect = pygame.Rect(row, col, grid_square_size, grid_square_size)
            blue = (50, 153, 213)
            pygame.draw.rect(display, blue, rect, 1)


def display_fruit_eaten_score(score: int):
    white = (255, 255, 255)
    score_font = pygame.font.SysFont("Cooper", grid_square_size * 2)
    score_text = score_font.render("Score: " + str(score), True, white)
    display.blit(score_text, (display_width / 9, display_height / 9))


def display_number_of_hits(hits: int):
    white = (255, 255, 255)
    score_font = pygame.font.SysFont("Cooper", grid_square_size * 2)
    score_text = score_font.render("Hits: " + str(hits), True, white)
    display.blit(score_text, (display_width / 1.3, display_height / 9))


def display_laser_collision_score(laser_hits: int):
    white = (255, 255, 255)
    score_font = pygame.font.SysFont("Cooper", int(grid_square_size * 1.50))
    score_text = score_font.render("Snakes Killed: " + str(laser_hits), True, white)
    display.blit(score_text, (display_width / 2.8, display_height / 11))

def display_timer(time: int):
    white = (255, 255, 255)
    score_font = pygame.font.SysFont("Cooper", grid_square_size)
    score_text = score_font.render(str(time), True, white)
    display.blit(score_text, (display_width / 1.13, display_height / 43))


def check_failure_state(snake, bad_snakes, result_metrics):
    failed_game = False
    if snake.has_eaten_itself is True or snake.is_out_of_bounds is True:
        failed_game = True
        result_metrics["number_of_game_failures"] += 1
        score = snake.length - 2
        result_metrics["scores_per_game"] += [score]
        result_metrics["snakes_killed_per_game"] += [bad_snakes.snakes_killed]
        result_metrics["hits_per_game"] += [bad_snakes.score]
        pygame.display.update()
    return failed_game


def run_game(start, result_metrics, file_name):
    game_over = False
    failed_game = False
    snake_speed2 = 4

    snake = Snake(grid_square_size, display_width, display_height)
    food = Food(display, grid_square_size, 600, 600)
    food_arr = [food]
    counter = 0
    bad_snakes = BadSnakes(grid_square_size, display_width, display_height)
    bad_snake_len = 1

    game_grid_area = (display_width / grid_square_size) * (display_height / grid_square_size)
    max_foods = game_grid_area / 20  # up to 5% of game grid filled with fruits at most

    def generate_new_food(loop_count: int):
        if loop_count % 25 == 0 and len(food_arr) < max_foods:
            new_food = Food(display, grid_square_size, 600, 600)
            food_arr.append(new_food)

    while not game_over:

        counter += 1
        fail_message_duration = 2000  # maybe add a break-out flag

        while failed_game:
            yellow = (255, 255, 0)
            message = font.render("You have failed the game! Press R to restart or Q to quit", True, yellow)
            if snake.has_eaten_itself:
                message = font.render("Game Over! Your snake has eaten itself!", True, yellow)
            elif snake.is_out_of_bounds:
                message = font.render("Game Over! Your snake is out of bounds!", True, yellow)

            if fail_message_duration > 0:
                display.blit(message, (display_width / 8, display_height / 2))
                pygame.display.update()
                fail_message_duration -= 1

                if time.time() - start > 90:
                    break
                else:
                    continue

            # reset game stats
            bad_snakes.snakes = []
            run_game(start, result_metrics, file_name)

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LSHIFT]:
            snake_speed2 = 7
        else:
            snake_speed2 = 4

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT:
                    snake.direction = Direction.RIGHT
                elif event.key == pygame.K_LEFT:
                    snake.direction = Direction.LEFT
                elif event.key == pygame.K_UP:
                    snake.direction = Direction.UP
                elif event.key == pygame.K_DOWN:
                    snake.direction = Direction.DOWN
                elif event.key == pygame.K_a:
                    failed_game = True
                elif event.key == pygame.K_SPACE:
                    snake.laser_state = "active"
                    laser = Laser2(grid_square_size, display_height, display_width)
                    snake.lasers.append(laser)

        display.fill('black')
        create_game_grid()
        display_fruit_eaten_score(snake.length - 2)
        display_number_of_hits(bad_snakes.score)
        display_laser_collision_score(bad_snakes.snakes_killed)
        display_timer(90 - int(time.time() - start))

        snake.generate_snake_body(display)
        generate_new_food(counter)
        bad_snakes.generate_snakes(display)

        # shows user where their snake is
        good_snake_identifier = font2.render("ME", True, (255, 0, 0))
        s_head = snake.body[-1]
        display.blit(good_snake_identifier, (s_head.centerx, s_head.centery))

        for fruit in food_arr:
            fruit.generate_food()
            snake.eat_food(fruit)

        snake.move_snake()
        bad_snakes.move_snakes()
        bad_snakes.hit_player_snake(snake.body)
        bad_snake_len = bad_snakes.generate_new_snakes(bad_snake_len)

        # the laser state is active as long as there is at least 1 laser in the laser array
        if snake.laser_state == "active":

            if len(snake.lasers) == 0:
                snake.laser_state = "inactive"
            else:
                snake_head = snake.body[-1]
                for las in list(snake.lasers):
                    laser_pos = las.generate_laser(display, snake.direction, snake_head.x, snake_head.y)
                    las.check_out_of_bounds()
                    laser_success = bad_snakes.check_laser_hits(laser_pos[0], laser_pos[1])
                    if las.out_of_bounds or laser_success:
                        snake.lasers.remove(las)

        failed_game = check_failure_state(snake, bad_snakes, result_metrics)

        if time.time() - start > 90:
            game_over = True
            score = snake.length - 2
            result_metrics["scores_per_game"] += [score]  # something strange about this
            result_metrics["snakes_killed_per_game"] += [bad_snakes.snakes_killed]
            result_metrics["hits_per_game"] += [bad_snakes.score]

        pygame.display.update()
        clock.tick(snake_speed2)

    pygame.quit()
    print("Advanced Snake Hand")
    print(result_metrics)
    f = open(file_name, "a")
    f.write("\nAdvanced game hand-controlled metrics " + str(result_metrics))
    f.close()
    sys.exit()
