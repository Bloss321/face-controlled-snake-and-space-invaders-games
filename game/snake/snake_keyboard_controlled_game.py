import time

import pygame

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
snake_speed = 3


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
    text = font.render("Time Left: " + str(time), True, white)
    display.blit(text, (500, 15))


def check_failure_state(snake: Snake, result_metrics):
    failed_game = False  # failed game if snake out of bounds or snake eats its own tail
    if snake.has_eaten_itself is True or snake.is_out_of_bounds is True:
        failed_game = True
        result_metrics["number_of_game_failures"] += 1
        score = snake.length - 2
        result_metrics["scores_per_game"] += [score]
        pygame.display.update()
    return failed_game


# ensure display always set at same value when returning to game
def update_global_screen():
    global display
    screen = pygame.display.set_mode((display_width, display_height))
    display = screen

# ADDED!
def generate_new_food(loop_count: int, food_arr, display):
    game_grid_area = (display_width / grid_square_size) * (display_height / grid_square_size)
    max_foods = game_grid_area / 10  # up to 10% of game grid filled with fruits at most
    if loop_count % 500 == 0 and len(food_arr) < max_foods:
        new_food = Food(display, grid_square_size, display_width, display_height)
        food_arr.append(new_food)
    return food_arr


def run_game(result_metrics, file_name):
    update_global_screen()
    game_over = False
    failed_game = False
    counter = 0

    snake = Snake(grid_square_size, display_width, display_height)
    food = Food(display, grid_square_size, display_width, display_height)
    food_arr = [food]

    from game.countdown.game_countdown import start_game_countdown

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

                # break if time over 2 minutes and game is over
                if time.time() - start > 120:
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
            if event.type == pygame.QUIT:
                game_over = True

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    game_over = True

            # keyboard-controlled logic, snake moves direction after single keypress from user
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
        display_timer(120 - int(time.time() - start))

        # generate game assets
        snake.generate_snake_body(display)
        # generate_new_food(counter)
        food_arr = generate_new_food(counter, food_arr, display)

        for fruit in food_arr:
            fruit.generate_food()
            snake.eat_food(fruit)

        # reduce speed of snake, only update position ever 20 frames
        if counter % 20 == 0:
            snake.move_snake()

        failed_game = check_failure_state(snake, result_metrics)

        # game ends once timer hits 2 minutes
        if time.time() - start > 120:
            game_over = True
            score = snake.length - 2
            result_metrics["scores_per_game"] += [score]

        pygame.display.update()
        clock.tick(60)

    print("Keyboard-controlled Snake Game")
    print(result_metrics)
    f = open(file_name, "a")
    f.write("\nKeyboard-controlled Snake Game metrics " + str(result_metrics))
    f.close()
