
import time

import pygame

from game.countdown.game_countdown import start_game_countdown
from game.snake.helper import Direction
from game.snake.snake import Snake
from game.snake.food import Food

pygame.init()

display_width = 800
display_height = 600
grid_square_size: int = 50

font = pygame.font.SysFont("Comic Sans",
                           int(grid_square_size / 2))

display = pygame.display.set_mode((display_width, display_height))
pygame.display.set_caption('Hand-controlled Snake Game via keyboard')

clock = pygame.time.Clock()
snake_speed = 3.8


def increase_snake_speed():
    global snake_speed
    snake_speed += 0.1


def create_game_grid():
    for row in range(0, display_width, grid_square_size):
        for col in range(0, display_height, grid_square_size):
            rect = pygame.Rect(row, col, grid_square_size, grid_square_size)
            blue = (50, 153, 213)
            pygame.draw.rect(display, blue, rect, 1)


def display_score(score: int):
    white = (255, 255, 255)
    score_font = pygame.font.SysFont("Cooper", grid_square_size * 2)
    score_text = score_font.render(str(score), True, white)
    display.blit(score_text, (display_width / 2.1, display_height / 9))


def display_timer(time: int):
    white = (255, 255, 255)
    font = pygame.font.SysFont("Cooper", grid_square_size)
    text = font.render(str(time), True, white)
    display.blit(text, (display_width / 1.13, display_height / 43))


def check_failure_state(snake: Snake, result_metrics):
    failed_game = False
    if snake.has_eaten_itself is True or snake.is_out_of_bounds is True:  # extract this method for testing
        failed_game = True
        result_metrics["number_of_game_failures"] += 1
        score = snake.length - 2
        result_metrics["scores_per_game"] += [score]
        pygame.display.update()
    return failed_game


def run_game(result_metrics, file_name):
    game_over = False
    failed_game = False
    counter = 0

    snake = Snake(grid_square_size, display_width, display_height)
    food = Food(display, grid_square_size, display_width, display_height)  # was 600, 600
    food_arr = [food]

    game_grid_area = (display_width / grid_square_size) * (display_height / grid_square_size)
    max_foods = game_grid_area / 10  # up to 10% of game grid filled with fruits at most

    def generate_new_food(loop_count: int):
        if loop_count % 25 == 0 and len(food_arr) < max_foods:
            new_food = Food(display, grid_square_size, display_width, display_height)
            food_arr.append(new_food)

    # start 3-second countdown at beginning of game
    if counter == 0:
        start_game_countdown(display, display_width, display_height)
        print("Countdown Finished.")
    start = time.time()
    while not game_over:

        counter += 1

        if (time.time() - start) % 10 == 0:
            increase_snake_speed()

        start_fail_timer = time.time()
        while failed_game:

            yellow = (255, 255, 0)
            message = font.render("You have failed the game!", True, yellow)
            if snake.has_eaten_itself:
                message = font.render("Game Over! Your snake has eaten itself!", True, yellow)
            elif snake.is_out_of_bounds:
                message = font.render("Game Over! Your snake is out of bounds!", True, yellow)

            if time.time() - start_fail_timer < 2:  # display failure message for 2 seconds
                display.blit(message, (display_width / 7, display_height / 20))
                pygame.display.update()

                if time.time() - start > 90:
                    break
                else:
                    continue
            else:
                # reset game stats
                snake = Snake(grid_square_size, display_width, display_height)
                food = Food(display, grid_square_size, display_width, display_height)
                food_arr = [food]
                break

        for event in pygame.event.get():
            # remove in final version
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

        display.fill('black')
        create_game_grid()
        display_score(snake.length - 2)
        display_timer(90 - int(time.time() - start))

        snake.generate_snake_body(display)
        generate_new_food(counter)

        for fruit in food_arr:
            fruit.generate_food()
            snake.eat_food(fruit)

        snake.move_snake()

        failed_game = check_failure_state(snake, result_metrics)

        if time.time() - start > 90:
            game_over = True
            score = snake.length - 2
            result_metrics["scores_per_game"] += [score]  # something strange about this

        pygame.display.update()
        clock.tick(snake_speed)

    print("Keyboard-controlled Snake Game")
    print(result_metrics)
    f = open(file_name, "a")
    f.write("\nKeyboard-controlled Snake Game metrics " + str(result_metrics))
    f.close()
