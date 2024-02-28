import time
import psutil

if __name__ == '__main__':

    file_name = "Test.txt"

    simple_game_result_metrics = {
        "number_of_game_failures": 0,
        "scores_per_game": [],  # number of fruit eaten
    }

    advanced_game_result_metrics = {
        "number_of_game_failures": 0,
        "scores_per_game": [],  # number of fruit eaten
        "snakes_killed_per_game": [],
        "hits_per_game": []
    }

    # Track system resources
    def display_system_resources():
        cpu_percent = psutil.cpu_percent()
        memory_info = psutil.virtual_memory()
        disk_info = psutil.disk_usage('/')

        print(f"CPU Usage: {cpu_percent}%")
        print(f"Memory Usage: {memory_info.percent}%")
        print(f"Disk Usage: {disk_info.percent}%")
        print("-" * 30)


    def simple_hand_controlled_game():
        import game.snake.simple.simple_snake_hand_controlled as simple_hand
        simple_hand.run_game(time.time(), simple_game_result_metrics, file_name)

    def mp_simple_face_controlled_game():
        import game.snake.simple.mp_simple_snake as mp_simple_face
        mp_simple_face.run_game(time.time(), simple_game_result_metrics, file_name)


    def simple_face_detection_game():
        import cv2
        import game.snake.simple.simple_snake_with_face_detection as simple_face
        from game.snake.common.face_detector_logic import Calibrate

        c = Calibrate()
        calibration_results = c.general_calibration(cv2.VideoCapture(0))
        simple_face.run_game_with_face_detector(time.time(), simple_game_result_metrics, calibration_results, file_name)

    def legacy_simple_face_detection_game():
        import cv2
        import game.snake.simple.mp_simple_snake_remove_lagging as sF
        from game.snake.common.face_detector_logic import Calibrate

        c = Calibrate()
        sF.run_game(time.time(), simple_game_result_metrics, file_name)

    def hpe_simple_face_detection_game():
        import cv2
        import game.snake.simple.mp_simple_snake_hpe as sF
        from game.snake.common.face_detector_logic import Calibrate

        c = Calibrate()
        sF.run_game(time.time(), simple_game_result_metrics, file_name)


    def advanced_hand_controlled_game():
        import game.snake.advanced.advanced_snake_game_hand_controlled as advanced_hand
        advanced_hand.run_game(time.time(), advanced_game_result_metrics, file_name)


    def advanced_face_detection_game():
        import cv2
        from game.snake.common.face_detector_logic import Calibrate
        import game.snake.advanced.advanced_snake_face_detection as advanced_face

        c = Calibrate()
        calibration_results = c.general_calibration(cv2.VideoCapture(0))
        advanced_face.run_game_with_detector_adv(time.time(), advanced_game_result_metrics, calibration_results,
                                                 file_name)


    def mp_advanced_face_detection_game():
        import cv2
        import mediapipe as mp
        from game.snake.common.face_detector_logic_mediapipe import Calibrate
        import game.snake.advanced.advanced_snake_face_detection_mediapipe as mp_advanced_face

        mp_face_mesh = mp.solutions.face_mesh
        face_mesh = mp_face_mesh.FaceMesh()

        mp_file_name = "mp_test.txt"

        c = Calibrate()
        calibration_results = c.general_calibration(cv2.VideoCapture(0), face_mesh, mp_face_mesh)
        mp_advanced_face.run_game_with_detector_adv(time.time(), advanced_game_result_metrics, calibration_results,
                                                    mp_file_name)

    def space_invaders():
        import game.space_invaders.hand_controlled_game as hand_space_invaders
        hand_space_invaders.run_game()

    def mp_space_invaders():
        import game.space_invaders.face_tracking_game as face_tracking_space_invaders
        face_tracking_space_invaders.run_game()

    # hpe_simple_face_detection_game()
    # legacy_simple_face_detection_game()
    # mp_simple_face_controlled_game()
    # mp_space_invaders()
    space_invaders()

    '''

    print("Welcome to the Snake game, here are your options.\n 1. Simple hand-controlled game"
          "\n 2. Simple face-tracking game\n 3. Advanced hand-controlled game "
          "\n 4. Advanced face-tracking game \n 5. MediaPipe Simple face-tracking game"
          "\n 6. Space Invaders hand-controlled game \n 7. Space Invaders face-tracking game")

    while True:
        if keyboard.is_pressed("1"):
            simple_hand_controlled_game()
            break
        elif keyboard.is_pressed("2"):
            simple_face_detection_game()
            break
        elif keyboard.is_pressed("3"):
            advanced_hand_controlled_game()
            break
        elif keyboard.is_pressed("4"):
            advanced_face_detection_game()
            break
        elif keyboard.is_pressed("5"):
            mp_simple_hand_controlled_game()
            break
        elif keyboard.is_pressed("6"):
            space_invaders()
            break
        elif keyboard.is_pressed("7"):
            mp_space_invaders()
            break
            '''
