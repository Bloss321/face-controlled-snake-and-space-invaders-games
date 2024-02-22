from statistics import mean

import pygame
import cv2
import mediapipe as mp
import numpy as np
import sys

from pygame import mixer

from game.space_invaders.alien import Alien
from game.space_invaders.laser import Laser
from game.space_invaders.player import Player

pygame.init()

display = pygame.display.set_mode((1120, 600))  # width was 800

background = pygame.image.load('game/space_invaders/background.png')

# mixer.music.load("background.wav")
# mixer.music.play(-1)

pygame.display.set_caption("Space Invaders")
# icon = pygame.image.load('game/space_invaders/ufo.png')
# pygame.display.set_icon(icon)
font = pygame.font.Font('freesansbold.ttf', 32)


def display_score(score: int):
    score = font.render("Score : " + str(score), True, (255, 255, 255))
    display.blit(score, (10, 10))


def display_game_over():
    game_over_font = pygame.font.Font('freesansbold.ttf', 64)
    over_text = game_over_font.render("GAME OVER", True, (255, 255, 255))
    display.blit(over_text, (200, 250))


def resize_video_output(frame, scale):  # scale given as decimal e.g. 0.75
    height = int(frame.shape[0] * scale)
    width = int(frame.shape[1] * scale)
    new_dimension = (width, height)
    return cv2.resize(frame, new_dimension, interpolation=cv2.INTER_AREA)


# add sounds to game later

def run_game():
    player = Player()  # maybe make laser a player attribute?
    aliens = [Alien() for _ in range(6)]
    laser = Laser()
    score = 0

    # window_name = "Mediapipe Face Tracker - Space Invaders"
    # cv2.namedWindow(window_name)
    # Initialize MediaPipe
    mp_face_mesh = mp.solutions.face_mesh
    # Initialize webcam
    cap = cv2.VideoCapture(0)
    frame_count = 0
    neutral_roll_angles = []
    neutral_lips_inner_dist = []
    direction = "neutral"

    clock = pygame.time.Clock()
    game_over = False

    with mp_face_mesh.FaceMesh(min_detection_confidence=0.5, min_tracking_confidence=0.5) as face_mesh:
        while not game_over:
            ret, frame = cap.read()
            if not ret:
                break

            # Flip the frame horizontally for a later selfie-view display
            frame = cv2.flip(frame, 1)
            # Convert the BGR image to RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # Process the frame with MediaPipe Face Mesh
            results = face_mesh.process(rgb_frame)

            # Draw landmarks on the face
            if results.multi_face_landmarks:
                for face_landmarks in results.multi_face_landmarks:

                    # draw the face mesh
                    for connection in mp_face_mesh.FACEMESH_TESSELATION:
                        edge1, edge2 = connection
                        start_point = face_landmarks.landmark[edge1]
                        end_point = face_landmarks.landmark[edge2]
                        # Convert normalized coordinates to pixel coordinates
                        ih, iw, _ = rgb_frame.shape
                        start_x, start_y = int(start_point.x * iw), int(start_point.y * ih)
                        end_x, end_y = int(end_point.x * iw), int(end_point.y * ih)
                        # Draw line between landmarks
                        cv2.line(rgb_frame, (start_x, start_y), (end_x, end_y), (0, 255, 0), 2)

                    # Extract relevant facial landmarks for head pose estimation
                    landmarks = np.array([[point.x, point.y, point.z] for point in face_landmarks.landmark])
                    # Calculate the direction vectors for roll (tilting)
                    roll_vector = landmarks[33] - landmarks[2]
                    # Calculate angles using dot products
                    roll_angle = np.arcsin(roll_vector[0] / np.linalg.norm(roll_vector))
                    # Convert angles from radians to degrees
                    roll_degrees = np.degrees(roll_angle)
                    # Display tilt angles
                    cv2.putText(rgb_frame, f"Direction: {direction}", (20, 100), cv2.FONT_HERSHEY_SIMPLEX, 1.5,
                                (255, 0, 0),
                                2)

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

                    # detect if mouth is open for triggering the shield

                    # mesh landmark locations for upper & lower inner lips
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

                    def is_mouth_open(neutral_inner_lips_dist: list):
                        mean_neutral_inner_lips_dist = mean(neutral_inner_lips_dist)
                        # find the absolute distances between corresponding landmarks for the upper & lower inner lips
                        if mean_lips_inner_dist - mean_neutral_inner_lips_dist > 0.018:
                            return True
                        else:
                            return False

                    if frame_count < 50:
                        neutral_roll_angles.append(roll_degrees)
                        neutral_lips_inner_dist.append(mean_lips_inner_dist)
                    else:
                        avg_neutral_roll_angle = np.mean(neutral_roll_angles)
                        if roll_degrees > avg_neutral_roll_angle and abs(avg_neutral_roll_angle) - abs(
                                roll_degrees) >= 4:
                            num = abs(avg_neutral_roll_angle) - abs(roll_degrees)
                            direction = "right " + str(num)
                            if abs(avg_neutral_roll_angle) - abs(roll_degrees) >= 20:
                                player.x_change = 15  # speed boost
                            else:
                                player.x_change = 5  # was -5
                        elif roll_degrees < avg_neutral_roll_angle and abs(roll_degrees) - abs(
                                avg_neutral_roll_angle) >= 4:
                            num = abs(roll_degrees) - abs(avg_neutral_roll_angle)
                            direction = "left " + str(num)
                            if abs(roll_degrees) - abs(avg_neutral_roll_angle) >= 24:
                                player.x_change = -15
                            else:
                                player.x_change = -5  # was -5
                        else:
                            player.x_change = 0

                        if smile_detected(0.54):
                            direction = direction + " , Smiling"
                            if laser.state == "inactive":
                                laser.x_pos = player.x_pos
                                laser.fire()

                        if is_mouth_open(neutral_lips_inner_dist):
                            direction = direction + " , Mouth Open"
                            player.shield_activated = True
                            player.is_shield_activated()
                        else:
                            player.shield_activated = False
                            player.is_shield_activated()

                        """# check for tilting for directions
                        if roll_degrees >= -28:  # if player tilts head to right
                            direction = "right"
                            player.x_change = 5
                        elif roll_degrees <= -39:  # if player tilts head to left
                            direction = "left"
                            player.x_change = -5
                        else:
                            player.x_change = 0

                        if smile_detected(0.54):
                            if laser.state == "inactive":
                                laser.x_pos = player.x_pos
                                laser.fire()"""

            frame_count += 1
            # frame_60 = resize_video_output(frame, 0.5)
            # cv2.imshow(window_name, frame_60)
            # cv2.moveWindow(window_name, 10, 50)  # this seems to work

            display.fill((0, 0, 0))
            display.blit(background, (0, 0))

            # all this logic can go in separate function so that code can be used for CV game
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    game_over = True
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        player.x_change = -5
                    if event.key == pygame.K_RIGHT:
                        player.x_change = 5
                    if event.key == pygame.K_SPACE:
                        '''if laser.state == "inactive":
                            laser.x_pos = player.x_pos
                            laser.fire()'''
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                        player.x_change = 0

            player.move()
            laser.move()

            for alien in aliens:
                alien.move()
                has_collided = laser.has_collided(alien)
                if has_collided:
                    laser.regenerate()
                    score += 1
                    alien.__init__()

            if any(alien.y_pos > 440 for alien in aliens):
                display_game_over()
                break

            player.generate(display)
            laser.generate(display)
            for alien in aliens:
                alien.generate(display)
            display_score(score)

            frame_60 = resize_video_output(rgb_frame, 0.5)
            rgb_frame = frame_60
            rgb_frame = np.flip(rgb_frame, 0)  # mirror the video stream
            rgb_frame = np.rot90(rgb_frame, 3)  # rotate the video stream so its upwards
            rgb_frame = pygame.surfarray.make_surface(rgb_frame)  # apply footage as pygame surface
            display.blit(rgb_frame, (800, 0))  # add video stream to game window

            pygame.display.update()
            clock.tick(60)

        cap.release()
        pygame.quit()


if __name__ == "__main__":
    run_game()
