import time

import joblib
import pygame
import cv2
import mediapipe as mp
import numpy as np
import warnings
import sklearn
import scipy.special._cdflib

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

display = pygame.display.set_mode((1120, display_height))
pygame.display.set_caption('Head-controlled Snake Game')

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
    score_font = pygame.font.SysFont("Cooper", grid_square_size)
    score_text = score_font.render("Time Left: " + str(time), True, white)
    display.blit(score_text, (500, 15))


def check_failure_state(snake: Snake, result_metrics):
    failed_game = False
    if snake.has_eaten_itself is True or snake.is_out_of_bounds is True:
        failed_game = True
        result_metrics["number_of_game_failures"] += 1
        score = snake.length - 2
        result_metrics["scores_per_game"] += [score]
        pygame.display.update()
    return failed_game


# rescale output video showing facial landmarks
def resize_video_output(frame, scale):  # scale given as decimal e.g. 0.75
    height = int(frame.shape[0] * scale)
    width = int(frame.shape[1] * scale)
    new_dimension = (width, height)
    return cv2.resize(frame, new_dimension, interpolation=cv2.INTER_AREA)


def update_global_screen():
    global display
    screen = pygame.display.set_mode((1120, display_height))
    display = screen


def run_game(result_metrics, file_name):
    update_global_screen()

    game_over = False
    failed_game = False
    counter = 0
    game_counter = 0

    snake = Snake(grid_square_size, display_width, display_height)
    food = Food(display, grid_square_size, display_width,
                display_height)
    food_arr = [food]

    game_grid_area = (display_width / grid_square_size) * (display_height / grid_square_size)
    max_foods = game_grid_area / 10  # up to 10% of game grid filled with fruits at most

    def generate_new_food(loop_count: int):
        if loop_count % 500 == 0 and len(food_arr) < max_foods:  # add fruit every 500 frames
            new_food = Food(display, grid_square_size, display_width, display_height)
            food_arr.append(new_food)

    # Load SVR models from .pkl files
    svr_pitch = joblib.load('game/regression_models/svr_pitch_model.pkl')
    svr_yaw = joblib.load('game/regression_models/svr_yaw_model.pkl')
    svr_roll = joblib.load('game/regression_models/svr_roll_model.pkl')
    warnings.filterwarnings('ignore',
                            message="X does not have valid feature names, but SVR was fitted with feature names",
                            category=UserWarning)

    # Initialize MediaPipe
    mp_face_mesh = mp.solutions.face_mesh

    # Initialize webcam
    cap = cv2.VideoCapture(0)
    face_mesh = mp_face_mesh.FaceMesh(max_num_faces=1, min_detection_confidence=0.5, min_tracking_confidence=0.5)

    # start 3-second countdown at beginning of game
    if game_counter == 0:
        start_game_countdown(display, 1120, display_height)

    start = time.time()
    while cap.isOpened() and not game_over:  # game runs whilst webcam is opened and game isn't over
        game_counter += 1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    game_over = True

        ret, frame = cap.read()
        if not ret:
            break

        # flip the frame horizontally for mirrored view so user's right is mirrored view's right
        frame = cv2.flip(frame, 1)
        # Convert the BGR frame to RGB for Mediapipe to process
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        rgb_frame.flags.writeable = False
        # MediaPipe FaceMesh processing
        results = face_mesh.process(rgb_frame)
        rgb_frame.flags.writeable = True

        if results.multi_face_landmarks:

            for landmarks in results.multi_face_landmarks:
                for landmark in landmarks.landmark:
                    # Convert normalized coordinates to pixel coordinates
                    x = int(landmark.x * frame.shape[1])
                    y = int(landmark.y * frame.shape[0])

                    # Draw the point on the frame
                    cv2.circle(rgb_frame, (x, y), 2, (0, 255, 0), -1)

            # Extract landmarks from the first detected face
            landmarks = results.multi_face_landmarks[0].landmark

            # Extract 3D coordinates of facial landmarks
            landmarks_3d = np.array([[lm.x, lm.y, lm.z] for lm in landmarks]).flatten()

            # Predict head pose angles using SVR models
            pitch = np.degrees(svr_pitch.predict([landmarks_3d])[0])
            yaw = np.degrees(svr_yaw.predict([landmarks_3d])[0])
            roll = np.degrees(svr_roll.predict([landmarks_3d])[0])

            if pitch > 10:
                snake.direction = Direction.UP
                print("UP " + str(pitch))
            if pitch < -10:
                snake.direction = Direction.DOWN
                print("DOWN " + str(pitch))
            if yaw > 15 or roll < - 10:    # yaw movements tend to have large angles so set to 15
                snake.direction = Direction.LEFT
                print("LEFT " + str(yaw) + ", " + str(roll))
            if yaw < -15 or roll > 10:
                snake.direction = Direction.RIGHT
                print("RIGHT " + str(yaw) + str(pitch) + ", " + str(roll))

        counter += 1

        if (time.time() - start) % 10 == 0:
            increase_snake_speed()

        fail_message_duration = 2000  # 2 seconds to show failed game message
        start_failure_timer = pygame.time.get_ticks()
        while failed_game:

            yellow = (255, 255, 0)
            message = font.render("You have failed the game! Press R to restart or Q to quit", True, yellow)
            if snake.has_eaten_itself:
                message = font.render("Game Over! Your snake has eaten itself!", True, yellow)
            elif snake.is_out_of_bounds:
                message = font.render("Game Over! Your snake is out of bounds!", True, yellow)

            current_time = pygame.time.get_ticks()
            elapsed_time = current_time - start_failure_timer

            if elapsed_time < fail_message_duration:
                display.blit(message, (display_width / 7, display_height / 2.5))

            pygame.display.update()

            if elapsed_time >= fail_message_duration:
                if time.time() - start > 120:
                    break
                else:
                    # reset game stats
                    counter = 0
                    snake = Snake(grid_square_size, display_width, display_height)
                    food = Food(display, grid_square_size, display_width,
                                display_height)
                    food_arr = [food]
                    break

        display.fill('black')
        create_game_grid()
        display_score(snake.length - 2)
        display_timer(120 - int(time.time() - start))

        snake.generate_snake_body(display)
        generate_new_food(counter)

        for fruit in food_arr:
            fruit.generate_food()
            snake.eat_food(fruit)

        if game_counter % 12 == 0:
            snake.move_snake()

        failed_game = check_failure_state(snake, result_metrics)

        # game ends after 2 minutes
        if time.time() - start > 120:
            game_over = True
            score = snake.length - 2
            result_metrics["scores_per_game"] += [score]

        max_dimension = max(rgb_frame.shape[0], rgb_frame.shape[1])
        total_display_width = display.get_width()
        scale_value = round((total_display_width - display_width) / max_dimension, 3)

        frame_60 = resize_video_output(rgb_frame, scale_value)
        rgb_frame = frame_60
        rgb_frame = np.flip(rgb_frame, 0)  # mirror the video stream
        rgb_frame = np.rot90(rgb_frame, 3)  # rotate the video stream so its upwards
        rgb_frame = pygame.surfarray.make_surface(rgb_frame)  # apply footage as pygame surface
        display.blit(rgb_frame, (display_width, 0))  # add video stream to game window
        pygame.display.update()
        clock.tick(60)

    print("Face-controlled Snake Game")
    print(result_metrics)
    f = open(file_name, "a")
    f.write("\nFace-controlled Snake Game metrics " + str(result_metrics))
    f.close()

    cap.release()
