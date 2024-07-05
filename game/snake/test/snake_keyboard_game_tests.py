import pytest
import pygame
from pygame import Rect
from unittest.mock import patch

from game.snake.food import Food
from game.snake.helper import Direction
from game.snake.snake import Snake
from game.snake.snake_keyboard_controlled_game import check_failure_state, generate_new_food

pygame.init()

grid_square_size = 50
display_width = 800
display_height = 600


@pytest.fixture()
def display():
    return pygame.display.set_mode((display_width, display_height))


@pytest.fixture()
def snake():
    return Snake(grid_square_size, display_width, display_height)


@pytest.fixture()
def food():
    return Food(display, grid_square_size, display_width, display_height)


# tests for the snake generated in the game
def test_initial_snake_size(snake):  # maybe one function as test snake initialisation?
    assert snake.body == [Rect(150, 300, 50, 50)]  # 150 middle  = 300
    assert snake.length == 2  # starting snake has size 2 blocks head: (x_pos, y_pos) + body


def test_initial_snake_position(snake):
    assert snake.x_pos == 200
    assert snake.y_pos == 300


def test_generate_snake_body(snake):
    # patch used to mock pygame calls inside functions
    with patch('pygame.draw.rect') as mock_draw_rect:
        snake.generate_snake_body(display)
        mock_draw_rect.assert_called_once_with(
            display,  # display
            (0, 255, 0),  # snake is green
            pygame.Rect(150, 300, 50, 50)  # Rect arguments
        )


def test_move_snake(snake):
    snake.direction = Direction.LEFT  # when the snake is moved left once
    snake.move_snake()
    assert snake.body == [Rect(150, 300, 50, 50), Rect(100, 300, 50, 50)]


def test_snake_eat_food(snake, food):
    with patch('pygame.draw.rect') as mock_draw_rect:
        food.generate_food()
        mock_draw_rect.assert_called()

        food.x_pos = 150
        food.y_pos = 300
        initial_snake_len = snake.length
        snake.eat_food(food)
        assert snake.length == 1 + initial_snake_len == 3


def test_snake_out_of_bounds(snake):
    snake.body[-1].x = display_width + 1
    snake.body[-1].y = display_height + 1
    snake.move_snake()
    assert snake.is_out_of_bounds is True


def test_snake_collision_with_self(snake):
    snake.move_snake()    # [Rect(150, 300, 50, 50), Rect(100, 300, 50, 50)]
    snake.body[-1].x = 150
    snake.body[-1].y = 300
    snake.check_collisions()
    assert snake.has_eaten_itself is True


def test_check_failure_state_when_snake_collides_with_self(snake):
    result_metrics = {
        "number_of_game_failures": 0,
        "scores_per_game": [],  # number of fruit eaten
    }
    snake.has_eaten_itself = True
    with patch('pygame.display.update') as mock_display_update:
        check_failure_state(snake, result_metrics)
        mock_display_update.assert_called()
        assert result_metrics["number_of_game_failures"] == 1


def test_check_failure_state_when_snake_out_of_bounds(snake):
    result_metrics = {
        "number_of_game_failures": 0,
        "scores_per_game": [],  # number of fruit eaten
    }
    snake.is_out_of_bounds = True
    with patch('pygame.display.update') as mock_display_update:
        check_failure_state(snake, result_metrics)
        mock_display_update.assert_called()
        assert result_metrics["number_of_game_failures"] == 1


def test_check_failure_state_when_game_not_failed(snake):
    result_metrics = {
        "number_of_game_failures": 0,
        "scores_per_game": [],  # number of fruit eaten
    }
    snake.is_out_of_bounds = False
    snake.has_eaten_itself = False
    check_failure_state(snake, result_metrics)
    assert result_metrics["number_of_game_failures"] == 0


# tests for the food generated in the game
def test_generate_food(food):
    with patch('pygame.draw.rect') as mock_draw_rect:
        food.generate_food()

        # get arguments passed to pygame.draw.rect()
        args, kwargs = mock_draw_rect.call_args

        # can't test directly like snake.generate because food Rect positions are randomly generated
        # instead check if pygame.draw.rect() was called with the correct arguments
        assert args[0] == display
        assert args[1] == (255, 0, 0)  # food is red
        assert isinstance(args[2], pygame.Rect)  # 3rd arg is of type Rect
        assert args[2].width == 50  # food width
        assert args[2].height == 50  # food height (food.square_size)


# tests function in snake game that adds new apples to game board every 500 game loops
def test_generate_new_food():
    food_arr = [food]  # game-board currently has only one food item/apple
    game_loop_count = 1000
    generate_new_food(game_loop_count, food_arr, display)
    assert len(food_arr) == 2  # now another food item has been added to game-board
