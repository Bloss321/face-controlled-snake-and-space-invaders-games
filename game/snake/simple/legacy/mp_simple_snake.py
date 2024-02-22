import sys
import time

import pygame
import cv2
import mediapipe as mp
import numpy as np

from game.snake.common.face_detector_logic_mediapipe import resize_video_output
from game.snake.common.helper import Direction
from game.snake.common.snake import Snake
from game.snake.common.food import Food
from track_environment_variables.track_system_resources import display_system_resources

pygame.init()

display_width = 600
display_height = 600
grid_square_size: int = 50

font = pygame.font.SysFont("Comic Sans",
                           int(grid_square_size / 2))  # change name will change font - block_size*2 (size) !

display = pygame.display.set_mode((display_width, display_height))
pygame.display.set_caption('Hand-controlled Snake Game via keyboard')

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


def display_timer(time: int):
    white = (255, 255, 255)
    score_font = pygame.font.SysFont("Cooper", grid_square_size)
    score_text = score_font.render(str(time), True, white)
    display.blit(score_text, (display_width / 1.13, display_height / 43))


def check_failure_state(snake: Snake, result_metrics):
    failed_game = False
    if snake.has_eaten_itself is True or snake.is_out_of_bounds is True:  # extract this method for testing
        failed_game = True
        result_metrics["number_of_game_failures"] += 1
        score = snake.length - 2
        result_metrics["scores_per_game"] += [score]
        pygame.display.update()  # why am I calling this??
    return failed_game


def run_game(start, result_metrics, file_name):
    game_over = False
    failed_game = False
    counter = 0
    initial_time = time.time()  # 2024 added

    snake = Snake(grid_square_size, display_width, display_height)
    food = Food(display, grid_square_size, 600, 600)  # need to randomise starting pos in Food class
    food_arr = [food]

    game_grid_area = (display_width / grid_square_size) * (display_height / grid_square_size)
    max_foods = game_grid_area / 10  # up to 10% of game grid filled with fruits at most

    def generate_new_food(loop_count: int):
        if loop_count % 25 == 0 and len(food_arr) < max_foods:
            new_food = Food(display, grid_square_size, 600, 600)
            food_arr.append(new_food)

    detector_running = True
    window_name = "Mediapipe Face Tracker - Simple Snake Game"
    cv2.namedWindow(window_name)
    # Initialize MediaPipe
    mp_face_mesh = mp.solutions.face_mesh
    # Initialize webcam
    cap = cv2.VideoCapture(0)
    frame_count = 0
    neutral_roll_angles = []
    neutral_pitch_angles = []  # for nodding head up & down

    with mp_face_mesh.FaceMesh(min_detection_confidence=0.5, min_tracking_confidence=0.5) as face_mesh:
        while not game_over:
            if time.time() > initial_time + 5:
                display_system_resources()
                initial_time = time.time()

            ret, frame = cap.read()
            if not ret:
                break

            # Flip the frame horizontally for a later selfie-view display
            frame = cv2.flip(frame, 1)
            # Convert the BGR image to RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # Process the frame with MediaPipe Face Mesh
            results = face_mesh.process(rgb_frame)

            direction = "neutral"

            # Draw landmarks on the face
            if results.multi_face_landmarks:
                for face_landmarks in results.multi_face_landmarks:

                    # draw the face mesh
                    for connection in mp_face_mesh.FACEMESH_TESSELATION:
                        edge1, edge2 = connection
                        start_point = face_landmarks.landmark[edge1]
                        end_point = face_landmarks.landmark[edge2]
                        # Convert normalized coordinates to pixel coordinates
                        ih, iw, _ = frame.shape
                        start_x, start_y = int(start_point.x * iw), int(start_point.y * ih)
                        end_x, end_y = int(end_point.x * iw), int(end_point.y * ih)
                        # Draw line between landmarks
                        cv2.line(frame, (start_x, start_y), (end_x, end_y), (0, 255, 0), 2)

                    # Extract relevant facial landmarks for head pose estimation
                    landmarks = np.array([[point.x, point.y, point.z] for point in face_landmarks.landmark])
                    # Calculate the direction vectors for roll (tilting)
                    roll_vector = landmarks[33] - landmarks[2]
                    pitch_vector = landmarks[33] - (landmarks[27] + landmarks[28]) / 2
                    # Yaw: Left-right rotation (turning)
                    yaw_vector = landmarks[33] - landmarks[263]
                    # Calculate angles using dot products
                    roll_angle = np.arcsin(roll_vector[0] / np.linalg.norm(roll_vector))
                    pitch_angle = np.arcsin(pitch_vector[1] / np.linalg.norm(pitch_vector))
                    yaw_angle = np.arcsin(yaw_vector[0] / np.linalg.norm(yaw_vector))
                    # Convert angles from radians to degrees
                    roll_degrees = np.degrees(roll_angle)
                    pitch_degrees = np.degrees(pitch_angle)
                    yaw_degrees = np.degrees(yaw_angle)
                    # Display tilt angles
                    cv2.putText(frame, f"Yaw: {yaw_degrees:.2f}" + direction, (20, 150), cv2.FONT_HERSHEY_SIMPLEX,
                                1, (0, 255, 0),
                                2)
                    cv2.putText(frame, f"Pitch: {pitch_degrees:.2f}", (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1,
                                (0, 255, 0), 2)
                    if frame_count < 50:
                        print("is the frame count under 50 working?")
                        neutral_roll_angles.append(roll_degrees)
                        neutral_pitch_angles.append(pitch_degrees)
                    else:
                        print("is this working?")
                        # the roll and pitch angles when the user's head is in a neutral position
                        avg_neutral_roll_angle = np.mean(neutral_roll_angles)
                        avg_neutral_pitch_angle = np.mean(neutral_pitch_angles)
                        roll_angle_diff = abs(abs(avg_neutral_roll_angle) - abs(roll_degrees))
                        pitch_angle_diff = abs(pitch_degrees - avg_neutral_pitch_angle)
                        # I can check the position of the nose compared to the neutral position for the roll action,
                        # the position of the nose is likely to be the same? for the pitch action, there's likely to
                        # be a fairly extreme different in position of the centre of the nose
                        if roll_angle_diff > pitch_angle_diff:  # <-- this doesn't work
                            if roll_degrees > avg_neutral_roll_angle and abs(avg_neutral_roll_angle) - abs(
                                    roll_degrees) >= 4:
                                direction = "right"  # double check if it is the opposite
                                snake.direction = Direction.RIGHT
                            if roll_degrees < avg_neutral_roll_angle and abs(roll_degrees) - abs(
                                    avg_neutral_roll_angle) >= 4:
                                direction = "left"
                                snake.direction = Direction.LEFT
                        elif pitch_angle_diff > roll_angle_diff:
                            if pitch_degrees > avg_neutral_pitch_angle and pitch_degrees - avg_neutral_pitch_angle >= 3:
                                direction = "up"
                                snake.direction = Direction.UP
                            if pitch_degrees < avg_neutral_pitch_angle and avg_neutral_pitch_angle - pitch_degrees >= 5:
                                direction = "down"
                                snake.direction = Direction.DOWN

            frame_count += 1
            frame_60 = resize_video_output(frame, 0.5)
            cv2.imshow(window_name, frame_60)
            cv2.moveWindow(window_name, 10, 50)

            if frame_count >= 50:
                counter += 1
                fail_message_duration = 500  # maybe add a break-out flag
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

                        if time.time() - start > 90:
                            break
                        else:
                            continue

                    # reset game stats
                    failed_game = False

                    # run_game(start, result_metrics, file_name)

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

        pygame.quit()
        print("Simple Snake Hand")
        print(result_metrics)
        f = open(file_name, "a")
        f.write("\nSimple game hand-controlled metrics " + str(result_metrics))
        f.close()  # got rid of sys.exit

        cap.release()
        pygame.quit()
