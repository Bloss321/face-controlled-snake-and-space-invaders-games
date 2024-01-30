import unittest

from game.snake.advanced.bad_snakes import BadSnakes
from game.snake.common.snake import Snake
import game.snake.simple.simple_snake_hand_controlled as simple_hand
import game.snake.advanced.advanced_snake_game_hand_controlled as advanced_hand


class TestGameOverWhenSnakeHitsBoundary(unittest.TestCase):
    def testSimpleGame(self):
        snake = Snake(10, 50, 50)
        snake.is_out_of_bounds = True
        snake.has_eaten_itself = True

        result_metrics = {
            "number_of_game_failures": 0,
            "scores_per_game": [],  # number of fruit eaten
        }

        actual = simple_hand.check_failure_state(snake, result_metrics)
        self.assertEqual(actual, True)

    def testAdvancedGame(self):
        snake = Snake(10, 50, 50)
        bad_snakes = BadSnakes(10, 50, 50)
        snake.is_out_of_bounds = True
        snake.has_eaten_itself = True

        result_metrics = {
            "number_of_game_failures": 0,
            "scores_per_game": [],  # number of fruit eaten
            "snakes_killed_per_game": [],
            "hits_per_game": []
        }

        actual = advanced_hand.check_failure_state(snake, bad_snakes, result_metrics)
        self.assertEqual(actual, True)
