import sys

import cv2
import dlib
import pygame
import time

import tkinter as tk
from tkinter import messagebox

from game.snake.common.face_detector_logic import resize_video_output, translate_head_movement
from game.snake.common.helper import Direction
from game.snake.common.snake import Snake
from game.snake.common.food import Food

# Game logic

pygame.init()

display_width = 600
display_height = 600
grid_square_size: int = 50

font = pygame.font.SysFont("Comic Sans", int(grid_square_size / 2))

display = pygame.display.set_mode((display_width, display_height))
pygame.display.set_caption('Head-controlled Snake Game')

clock = pygame.time.Clock()
snake_speed = 4


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


def display_timer(timer: int):
    white = (255, 255, 255)
    score_font = pygame.font.SysFont("Cooper", grid_square_size)
    score_text = score_font.render(str(timer), True, white)
    display.blit(score_text, (display_width / 1.13, display_height / 43))


def pop_up_instructions(message):

    root = tk.Tk()
    root.withdraw()
    messagebox.showinfo("Calibration", message)
    root.mainloop()


def run_game_with_face_detector(start, result_metrics, calibration_results, file_name):
    # for landmark detector
    detector_running = True
    vid_capture = cv2.VideoCapture(0)
    window_name = "facial landmark detector - simple"  # added
    cv2.namedWindow(window_name)  # added
    face_detector = dlib.get_frontal_face_detector()
    face_landmark_predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

    initial_centre_point = calibration_results.get("centre_of_nose")  # (364, 255)
    new_centre_point = (0, 0)
    num_of_landmarks = 68
    counter = 0

    # for game
    game_over = False
    failed_game = False
    snake = Snake(grid_square_size, display_width, display_height)
    food = Food(display, grid_square_size, 600, 600)

    game_loop_counter = 0
    food_arr = [food]
    game_grid_area = (display_width / grid_square_size) * (display_height / grid_square_size)
    max_foods = game_grid_area / 10  # up to 10% of game grid filled with fruits at most

    def generate_new_food(loop_count: int):
        if loop_count % 25 == 0 and len(food_arr) < max_foods:
            new_food = Food(display, grid_square_size, 600, 600)
            food_arr.append(new_food)

    while not game_over:

        game_loop_counter += 1
        fail_message_duration = 500
        while failed_game:
            yellow = (255, 255, 0)
            message = font.render("You have failed the game! Press R to restart or Q to quit", True, yellow)
            if snake.has_eaten_itself:
                message = font.render("Game Over! Your snake has eaten itself!", True, yellow)
            elif snake.is_out_of_bounds:
                message = font.render("Game Over! Your snake is out of bounds!", True, yellow)

            if fail_message_duration > 0:
                display.blit(message, (display_width / 7, display_height / 2.5))
                pygame.display.update()
                fail_message_duration -= 1

                if time.time() - start > 95:
                    break
                else:
                    continue

            # reset game stats
            run_game_with_face_detector(start, result_metrics, calibration_results, file_name)

        while detector_running:

            if time.time() - start > 95:
                game_over = True
                score = snake.length - 2
                result_metrics["scores_per_game"] += [score]  # something strange about this
                break

            _, frame = vid_capture.read()
            frame = cv2.flip(frame, 1)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            faces = face_detector(gray)
            for face in faces:

                face_landmarks = face_landmark_predictor(gray, face)
                centre = face_landmarks.part(30)  # centre of the nose according to predictor (landmark 31)
                new_centre_point = (centre.x, centre.y)

                for n in range(0, num_of_landmarks):
                    x = face_landmarks.part(n).x
                    y = face_landmarks.part(n).y
                    cv2.circle(frame, (x, y), 1, (0, 255, 0), 1)

            frame_60 = resize_video_output(frame, 0.5)
            cv2.imshow(window_name, frame_60)
            cv2.moveWindow(window_name, 10, 50)  # this seems to work

            if counter == 0:
                snake.direction = Direction.RIGHT
            else:
                snake.direction = translate_head_movement(initial_centre_point, new_centre_point, snake.direction)
            print(str(initial_centre_point) + "  " + str(new_centre_point) + " " + str(snake.direction))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    game_over = True

            display.fill('black')
            create_game_grid()
            display_score(snake.length - 2)
            display_timer(95 - int(time.time() - start))

            snake.generate_snake_body(display)
            generate_new_food(game_loop_counter)

            for fruit in food_arr:
                fruit.generate_food()
                snake.eat_food(fruit)

            snake.move_snake()

            if snake.has_eaten_itself is True or snake.is_out_of_bounds is True:
                failed_game = True
                result_metrics["number_of_game_failures"] += 1
                score = snake.length - 2
                result_metrics["scores_per_game"] += [score]
                pygame.display.update()
                break

            pygame.display.update()
            clock.tick(snake_speed)

            initial_centre_point = new_centre_point

            counter += 1
            key = cv2.waitKey(1)
            if key == 27:
                break

        vid_capture.release()
        cv2.destroyAllWindows()

    pygame.quit()
    print("Simple Snake Face")
    print(result_metrics)
    f = open(file_name, "a")
    f.write("\nSimple game face-controlled metrics " + str(result_metrics))
    f.close()
    sys.exit()
