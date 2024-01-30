import sys
from statistics import mean

import pygame
import cv2
# import dlib
import mediapipe as mp
import time

from game.snake.advanced.Laser_2 import Laser2
from game.snake.advanced.bad_snakes import BadSnakes
from game.snake.common.face_detector_logic_mediapipe import mp_translate_head_movement
from game.snake.common.helper import Direction
from game.snake.common.snake import Snake
from game.snake.common.food import Food
from game.snake.common.face_detector_logic import translate_head_movement, resize_video_output, detect_smile
from game.snake.common.face_detector_logic import is_mouth_open

pygame.init()

display_width = 600  # 800?
display_height = 600
grid_square_size: int = 25  # 50

font = pygame.font.SysFont("Comic Sans", grid_square_size)  # change name will change font - block_size*2 (size) !
font2 = pygame.font.SysFont("Comic Sans", int(grid_square_size / 1.5))

display = pygame.display.set_mode((display_width, display_height))
pygame.display.set_caption('Head-controlled Snake Game')

clock = pygame.time.Clock()
snake_speed = 5


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
    score_font = pygame.font.SysFont("Cooper", int(grid_square_size * 1.25))
    score_text = score_font.render(str(time), True, white)
    display.blit(score_text, (display_width / 1.13, display_height / 43))


def run_game_with_detector_adv(start, result_metrics, mp_calibration_results: dict, file_name):
    # for landmark detector
    detector_running = True
    vid_capture = cv2.VideoCapture(0)
    window_name = "facial landmark detector - advanced"
    cv2.namedWindow(window_name)
    # face_detector = dlib.get_frontal_face_detector()
    # face_landmark_predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")
    mp_face_detection = mp.solutions.face_detection
    mp_face_mesh = mp.solutions.face_mesh
    # Initialize MediaPipe Face Detection module
    face_detection = mp_face_detection.FaceDetection(min_detection_confidence=0.3)
    # Initialize MediaPipe Face Mesh module
    face_mesh = mp_face_mesh.FaceMesh()

    nose_tip_x = mp_calibration_results.get("nose_tip_x")
    nose_tip_y = mp_calibration_results.get("nose_tip_y")

    initial_centre_point = (nose_tip_x, nose_tip_y)
    new_centre_point = (0, 0)
    # why do I need this here???
    counter = 0

    # for game
    game_over = False
    failed_game = False
    snake = Snake(grid_square_size, display_width, display_height)
    food = Food(display, grid_square_size, 600, 600)
    food_arr = [food]
    food_counter = 0
    bad_snakes = BadSnakes(grid_square_size, display_width, display_height)
    bad_snake_len = 1
    snake_speed2 = 3

    game_grid_area = (display_width / grid_square_size) * (display_height / grid_square_size)
    max_foods = game_grid_area / 20  # up to 5% of game grid filled with fruits at most

    def generate_new_food(loop_count: int):
        if loop_count % 25 == 0 and len(food_arr) < max_foods:
            new_food = Food(display, grid_square_size, 600, 600)
            food_arr.append(new_food)

    while not game_over:

        food_counter += 1
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

                if time.time() - start > 95:
                    break
                else:
                    continue

            # reset game stats
            run_game_with_detector_adv(start, result_metrics, mp_calibration_results, file_name)

        while detector_running:

            if time.time() - start > 95:
                game_over = True
                score = snake.length - 2
                result_metrics["scores_per_game"] += [score]  # something strange about this
                result_metrics["snakes_killed_per_game"] += [bad_snakes.snakes_killed]
                result_metrics["hits_per_game"] += [bad_snakes.score]
                break  # instead have something similar to fail game output

            ret, frame = vid_capture.read()  # once it gets here -  it reads None, there's no video object initialised!
            if not ret:
                break

            frame = cv2.flip(frame, 1)
            # Convert the BGR image to RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # Perform face detection
            detection_results = face_detection.process(rgb_frame)

            # Perform face mesh detection
            mesh_results = face_mesh.process(rgb_frame)

            if mesh_results.multi_face_landmarks:
                for landmarks in mesh_results.multi_face_landmarks:

                    # why is the centre of the face being calculated here?
                    # the calibration logic should ideally be moved
                    # only game logic here

                    # for now have mediapipe logic here
                    # nested for loop to extract landmarks from mesh
                    # these mesh landmarks are probed at every frame
                    # constantly compare with neutral positions to determine movement

                    centre = landmarks.landmark[4]  # centre of nose
                    new_centre_point = (centre.x, centre.y)

                    # draw the face mesh
                    for connection in mp_face_mesh.FACEMESH_TESSELATION:
                        edge1, edge2 = connection
                        start_point = landmarks.landmark[edge1]
                        end_point = landmarks.landmark[edge2]

                        # Convert normalized coordinates to pixel coordinates
                        ih, iw, _ = frame.shape
                        start_x, start_y = int(start_point.x * iw), int(start_point.y * ih)
                        end_x, end_y = int(end_point.x * iw), int(end_point.y * ih)

                        # Draw line between landmarks
                        cv2.line(frame, (start_x, start_y), (end_x, end_y), (0, 255, 0), 2)

                    # check if mouth open
                    # mesh landmark locations for upper & lower inner lips
                    mesh_lips_upper_inner = [78, 191, 80, 81, 82, 13, 312, 311, 310, 415, 308]
                    mesh_lips_lower_inner = [78, 95, 88, 178, 87, 14, 317, 402, 318, 324, 308]

                    lips_upper_inner_landmarks = []
                    for lip_landmark in mesh_lips_upper_inner:
                        lips_upper_inner_landmarks.append(landmarks.landmark[lip_landmark].y)
                    lips_lower_inner_landmarks = []
                    for lips_landmark in mesh_lips_lower_inner:
                        lips_lower_inner_landmarks.append(landmarks.landmark[lips_landmark].y)

                    # find the absolute distances between corresponding landmarks for the upper & lower inner lips
                    lips_inner_dist = [abs(x - y) for x, y in
                                       zip(lips_lower_inner_landmarks, lips_upper_inner_landmarks)]
                    mean_lips_inner_dist = mean(lips_inner_dist)

                    # check if mouth is open
                    if mean_lips_inner_dist - mp_calibration_results.get(
                            "avg_lips_inner_dist") > 0.018:  # hardcoded for now
                        snake.laser_state = "active"
                        laser = Laser2(grid_square_size, display_height, display_width)
                        snake.lasers.append(laser)

                    # check if smiling
                    # remove this logic elsewhere later

                    def detecting_smile(threshold):
                        ratio = detect_smile_ratio()

                        if ratio > threshold:
                            return True
                        else:
                            return False

                    def detect_smile_ratio():
                        left_corner = landmarks.landmark[61]
                        right_corner = landmarks.landmark[291]

                        smile_width = abs(left_corner.x - right_corner.x)
                        # landmarks for the top of the jaw on either side of the face
                        jaw_width = abs(landmarks.landmark[147].x - landmarks.landmark[401].x)
                        ratio = smile_width / jaw_width
                        return ratio

                    if detecting_smile(0.54):  # hardcoded for now
                        snake_speed2 = 7
                    else:
                        snake_speed2 = 3

            frame_60 = resize_video_output(frame, 0.5)
            cv2.imshow(window_name, frame_60)
            cv2.moveWindow(window_name, 10, 50)  # this seems to work

            # if counter == 0:
            if 4 > counter >= 0:  # gives player a chance to start moving
                snake.direction = Direction.RIGHT
            else:
                snake.direction = mp_translate_head_movement(initial_centre_point, new_centre_point, snake.direction)


            # NEED TO REMOVE!
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    game_over = True

            display.fill('black')
            create_game_grid()
            display_fruit_eaten_score(snake.length - 2)
            display_number_of_hits(bad_snakes.score)
            display_laser_collision_score(bad_snakes.snakes_killed)
            display_timer(95 - int(time.time() - start))

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

            # check if snake has been hit - NEW ADDITION
            for laser in snake.lasers:
                for bs in bad_snakes.snakes:
                    laser_pos = (laser.x_pos, laser.y_pos)
                    bs_pos = (bs.x_pos, bs.y_pos)
                    if laser_pos == bs_pos:
                        snake.lasers.remove(laser)
                        bad_snakes.snakes.remove(bs)
                        bad_snakes.snakes_killed += 1

            if snake.laser_state == "active":

                if len(snake.lasers) == 0:
                    snake.laser_state = "inactive"
                else:
                    snake_head = snake.body[-1]
                    for las in snake.lasers:  # list(snake.lasers):
                        las_pos = las.generate_laser(display, snake.direction, snake_head.x, snake_head.y)
                        if las.check_out_of_bounds():
                            snake.lasers.remove(las)
                        for bs in bad_snakes.snakes:
                            bs_pos = (bs.x_pos, bs.y_pos)
                            if las_pos == bs_pos:
                                snake.lasers.remove(las)
                                bad_snakes.snakes.remove(bs)
                                bad_snakes.snakes_killed += 1
                        # laser_success = bad_snakes.check_laser_hits(laser_pos[0], laser_pos[1])
                        # if las.out_of_bounds:  # or laser_success:
                            # snake.lasers.remove(las)

            if snake.has_eaten_itself is True or snake.is_out_of_bounds is True:
                failed_game = True
                result_metrics["number_of_game_failures"] += 1
                score = snake.length - 2
                result_metrics["scores_per_game"] += [score]
                result_metrics["snakes_killed_per_game"] += [bad_snakes.snakes_killed]
                result_metrics["hits_per_game"] += [bad_snakes.score]
                pygame.display.update()
                break

            pygame.display.update()
            clock.tick(snake_speed2)

            # initial_centre_point = new_centre_point # SHOULD BE COMPARED WITH NEUTRAL FACE

            counter += 1
            key = cv2.waitKey(1)
            if key == 27:
                break

        vid_capture.release()
        cv2.destroyAllWindows()
    pygame.quit()
    print("MediaPipe Advanced Snake Face")
    # print(result_metrics)
    f = open(file_name, "a")
    f.write("\nMediaPipe Advanced game face-controlled metrics " + str(result_metrics))
    f.close()
    sys.exit()
