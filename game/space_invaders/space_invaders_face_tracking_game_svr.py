import random
import time
from statistics import mean

import joblib
import pygame
import cv2
import mediapipe as mp
import numpy as np

from pygame import mixer

from game.countdown.game_countdown import start_game_countdown
from game.space_invaders.alien import Alien
from game.space_invaders.laser import Laser
from game.space_invaders.player import Player

pygame.init()

display_width = 1120
display_height = 600

display = pygame.display.set_mode((display_width, display_height))  # width was 800

background = pygame.image.load('game/space_invaders/images/background.png')

pygame.display.set_caption("Space Invaders")
font = pygame.font.Font('freesansbold.ttf', 32)


def display_score(score: int):
    score = font.render("Score : " + str(score), True, (255, 255, 255))
    display.blit(score, (10, 10))


def display_hits_from_invaders(hits: int):
    score = font.render("Hits : " + str(hits), True, (255, 255, 255))
    display.blit(score, (200, 10))


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


def resize_video_output(frame, scale):  # scale given as decimal e.g. 0.75
    height = int(frame.shape[0] * scale)
    width = int(frame.shape[1] * scale)
    new_dimension = (width, height)
    return cv2.resize(frame, new_dimension, interpolation=cv2.INTER_AREA)


# add sounds to game later

def run_game(result_metrics, file_name):
    player = Player()
    aliens = [Alien() for _ in range(6)]
    laser = Laser()
    laser.y_jumps = 13
    alien_laser = Laser()
    alien_laser.y_jumps = 13
    alien_laser.is_alien_laser = True
    score = 0
    hits_from_invaders = 0

    # Initialize MediaPipe
    mp_face_mesh = mp.solutions.face_mesh
    # Initialize webcam
    cap = cv2.VideoCapture(0)

    frame_count = 0
    counter = 0
    game_counter = 0
    direction = "neutral"

    clock = pygame.time.Clock()
    game_over = False
    failed_game = False

    # start 3-second countdown at beginning of game
    if counter == 0:
        start_game_countdown(display, display_width, display_height)

    svr_roll = joblib.load('face_tracking/head_pose_estimation/regression_models/svr_roll_model.pkl')

    start = time.time()
    with mp_face_mesh.FaceMesh(min_detection_confidence=0.5, min_tracking_confidence=0.5) as face_mesh:
        while not game_over:
            counter += 1
            game_counter += 1

            ret, frame = cap.read()
            if not ret:
                break

            # Flip the frame horizontally for a later selfie-view display
            frame = cv2.flip(frame, 1)
            # Convert the BGR image to RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # Process the frame with MediaPipe Face Mesh
            rgb_frame.flags.writeable = False
            results = face_mesh.process(rgb_frame)
            rgb_frame.flags.writeable = True

            # Draw landmarks on the face
            if results.multi_face_landmarks:
                for face_landmarks in results.multi_face_landmarks:

                    landmarks = face_landmarks.landmark

                    # Extract 3D coordinates of facial landmarks
                    landmarks_3d = np.array([[lm.x, lm.y, lm.z] for lm in landmarks]).flatten()

                    # Predict head pose angles using SVR models
                    roll = np.degrees(svr_roll.predict([landmarks_3d])[0])

                    # detect smile for shooting lasers
                    def smile_detected(threshold):  # threshold  = 0.54
                        ratio = detect_smile_ratio()
                        if ratio > threshold:
                            return True
                        else:
                            return False

                    def detect_smile_ratio():
                        left_corner = face_landmarks.landmark[61]
                        right_corner = face_landmarks.landmark[291]

                        smile_width = abs(left_corner.x - right_corner.x)
                        # landmarks for the top of the jaw on either side of the face
                        jaw_width = abs(face_landmarks.landmark[147].x - face_landmarks.landmark[401].x)
                        ratio = smile_width / jaw_width
                        return ratio

                    # mesh landmark locations for upper & lower inner lips - logic for open mouth check
                    mesh_lips_upper_inner = [78, 191, 80, 81, 82, 13, 312, 311, 310, 415, 308]
                    mesh_lips_lower_inner = [78, 95, 88, 178, 87, 14, 317, 402, 318, 324, 308]
                    lips_upper_inner_landmarks = []
                    for lip_landmark in mesh_lips_upper_inner:
                        lips_upper_inner_landmarks.append(face_landmarks.landmark[lip_landmark].y)
                    lips_lower_inner_landmarks = []
                    for lips_landmark in mesh_lips_lower_inner:
                        lips_lower_inner_landmarks.append(face_landmarks.landmark[lips_landmark].y)
                    # find the absolute distances between corresponding landmarks for the upper & lower inner lips
                    lips_inner_dist = [abs(x - y) for x, y in
                                       zip(lips_lower_inner_landmarks, lips_upper_inner_landmarks)]
                    mean_lips_inner_dist = mean(lips_inner_dist)

                    # detect if mouth is open for triggering the shield
                    def is_mouth_open():
                        if mean_lips_inner_dist > 0.02:  # distances greater than 0.02 considered mouth open
                            return True
                        else:
                            return False

                    if roll > 20:
                        direction = "right"
                        player.x_change = 15  # speed boost for extreme right tilt
                    elif roll < -20:
                        direction = "left"
                        player.x_change = -15  # speed boost for extreme left tilt
                    elif roll > 10:
                        direction = "right"
                        player.x_change = 5
                    elif roll < -10:
                        direction = "left"
                        player.x_change = -5
                    else:
                        player.x_change = 0

                    if smile_detected(0.54):  # 0.54
                        direction = direction + " , Smiling"
                        if laser.state == "inactive":
                            laser.x_pos = player.x_pos
                            laser.fire()

                    if is_mouth_open() and player.shield_activated is False:
                        direction = direction + " , Mouth Open"
                        player.shield_activation_num += 1
                        if player.shield_activation_num > player.max_shield_activations:
                            max_shield_activations_text = font.render("Max Shield Activations Reached", True,
                                                                      (255, 255, 255))
                            display.blit(max_shield_activations_text, (350, 250))
                        else:
                            player.shield_activated = True
                            player.is_shield_activated()
                            start_shield_timer()

            frame_count += 1

            display.fill((0, 0, 0))
            display.blit(background, (0, 0))

            player.move()
            laser.move()
            alien_laser.move_alien_laser()

            if shield_timer_running:  # while the shield is activated
                elapsed_shield_time = time.time() - start_shield_time

                # shield is activated for 5 seconds
                if elapsed_shield_time >= 5:
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

            # every 50 frame counts an alien will randomly shoot a laser at the player
            if frame_count % 50 == 0:
                alien = random.choice(aliens)
                if alien_laser.state == "inactive":
                    alien_laser.x_pos = alien.x_pos
                    alien_laser.y_pos = alien.y_pos
                    alien_laser.fire()

            # check if the alien's laser has collided with a player
            has_collided_with_player = alien_laser.has_collided_with_player(player)
            if has_collided_with_player:
                hits_from_invaders += 1  # when the player is hit by an alien

            # if alien invaders reach bottom of screen
            if any(alien.y_pos > 440 for alien in aliens):
                failed_game = True
                result_metrics["number_of_game_failures"] += 1
                result_metrics["scores_per_game"] += [score]
                result_metrics["hits_from_invaders_per_game"] += [hits_from_invaders]

            start_fail_timer = time.time()
            while failed_game:
                yellow = (255, 255, 0)
                font2 = pygame.font.Font('freesansbold.ttf', 25)
                message = font2.render("Game Over! The Space Invaders have reached you!", True, yellow)
                if time.time() - start_fail_timer < 3:
                    display.blit(message, (150, 50))
                    pygame.display.update()
                else:
                    failed_game = False

                    if time.time() - start > 120:
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

            player.generate(display)
            laser.generate(display)
            alien_laser.generate(display)
            for alien in aliens:
                alien.generate(display)

            display_score(score)
            display_hits_from_invaders(hits_from_invaders)
            display_timer(120 - int(time.time() - start))

            if time.time() - start > 120:
                game_over = True
                result_metrics["scores_per_game"] += [score]
                result_metrics["hits_from_invaders_per_game"] += [hits_from_invaders]

            frame_60 = resize_video_output(rgb_frame, 0.5)
            rgb_frame = frame_60
            rgb_frame = np.flip(rgb_frame, 0)  # mirror the video stream
            rgb_frame = np.rot90(rgb_frame, 3)  # rotate the video stream so its upwards
            rgb_frame = pygame.surfarray.make_surface(rgb_frame)  # apply footage as pygame surface
            display.blit(rgb_frame, (800, 0))  # add video stream to game window

            pygame.display.update()
            clock.tick(60)

        cap.release()
        print("Face-controlled Space Invaders Game")
        print(result_metrics)
        f = open(file_name, "a")
        f.write("\nFace-controlled Space Invaders Game metrics " + str(result_metrics))
        f.close()
