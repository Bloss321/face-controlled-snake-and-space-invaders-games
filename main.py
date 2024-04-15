import time

import cv2
import pygame
import sys
import webbrowser

from pygame import Surface

if __name__ == '__main__':

    pygame.init()

    DISPLAY_WIDTH = 800  # set up display dimensions
    DISPLAY_HEIGHT = 800

    background_colour = (51, 102, 153)

    display = pygame.display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT))
    pygame.display.set_caption("Start Menu")

    # load start menu title image
    main_menu_title_original = pygame.image.load('game/menu/images/text/main menu title.png')
    # scale down menu title
    scale = (main_menu_title_original.get_width() // 1.5, main_menu_title_original.get_height() // 1.5)
    main_menu_title = pygame.transform.scale(main_menu_title_original, scale)

    # load buttons for questionnaires
    questionnaire_button = pygame.image.load('game/menu/images/buttons/questionnaire button.png')

    # load button images for games
    snake_keyboard_button = pygame.image.load('game/menu/images/buttons/snake keyboard.png')
    snake_face_button = pygame.image.load('game/menu/images/buttons/snake face.png')
    space_invaders_keyboard_button = pygame.image.load('game/menu/images/buttons/space invaders keyboard.png')
    space_invaders_face_button = pygame.image.load('game/menu/images/buttons/space invaders face.png')

    # load greyed-out button images
    snake_keyboard_grey_button = pygame.image.load('game/menu/images/buttons/grey/snake keyboard gray.png')
    snake_face_grey_button = pygame.image.load('game/menu/images/buttons/grey/snake face grey.png')
    space_invaders_keyboard_grey_button = pygame.image.load(
        'game/menu/images/buttons/grey/space invaders keyboard grey.png')
    space_invaders_face_grey_button = pygame.image.load('game/menu/images/buttons/grey/space invaders face grey.png')

    # order that games will be played in
    gameplay_order = ["snake keyboard", "snake face", "space invaders keyboard", "space invaders face"]
    current_game_idx = 0

    snake_game_result_metrics = {
        "number_of_game_failures": 0,
        "scores_per_game": [],  # number of fruit eaten
    }

    space_invaders_result_metrics = {
        "number_of_game_failures": 0,
        "scores_per_game": [],  # number of aliens hit successfully
        "hits_from_invaders_per_game": []  # number of times player is hit by alien laser per game
    }


    def get_button_rect_values(x_pos, y_pos, image: Surface):
        rect = image.get_rect()
        x = x_pos - rect.width / 2
        y = y_pos - rect.height / 2
        return x, y


    def display_image(x_pos, y_pos, button_image: Surface):
        top_left = get_button_rect_values(x_pos, y_pos, button_image)
        display.blit(button_image, top_left)


    def load_correct_game_buttons(current_game: str):
        buttons = {
            "snake keyboard": snake_keyboard_grey_button,
            "snake face": snake_face_grey_button,
            "space invaders keyboard": space_invaders_keyboard_grey_button,
            "space invaders face": space_invaders_face_grey_button
        }
        if current_game == "snake keyboard":
            buttons["snake keyboard"] = snake_keyboard_button
        elif current_game == "snake face":
            buttons["snake face"] = snake_face_button
        elif current_game == "space invaders keyboard":
            buttons["space invaders keyboard"] = space_invaders_keyboard_button
        elif current_game == "space invaders face":
            buttons["space invaders face"] = space_invaders_face_button

        return buttons


    def initialise_test_results_file(unique_id_file_path):
        # read a unique id from the text file
        with open(unique_id_file_path, 'r') as file:
            lines = file.readlines()
            unique_id = lines[0].strip()  # Remove leading and trailing whitespace

        # Read the remaining lines into memory
        with open(unique_id_file_path, 'r') as file:
            lines = file.readlines()[1:]  # Read all lines except the first one

        # Write the remaining lines back to the text file
        with open(unique_id_file_path, 'w') as file:
            file.writelines(lines)

        test_file_path = 'user_tests/test_data/' + unique_id + '.txt'
        with open(test_file_path, 'w') as file:
            # Write the content to the file
            file.write("Participant " + unique_id + " Game Metrics:")

        return unique_id, test_file_path


    # unique_id, file_name = initialise_test_results_file('user_tests/data/unused_unique_ids.txt')
    unique_id, file_name = "S", 'user_tests/test_data/S.txt'


    def main_menu():
        clock = pygame.time.Clock()
        back_button = pygame.image.load('game/menu/images/buttons/back.png')

        while True:
            # this should only run after the last game has been played
            if current_game_idx >= 4:
                end_of_games_page(time.time())
                pygame.quit()
                sys.exit()

            display.fill(background_colour)
            display_image(DISPLAY_WIDTH // 2, 150, main_menu_title)
            display_image(100, 750, back_button)

            # Initial positions of start menu buttons
            button_x = DISPLAY_WIDTH // 2
            button_y = 300

            game_buttons = load_correct_game_buttons(gameplay_order[current_game_idx])

            # display menu buttons for games
            display_image(button_x, button_y, game_buttons.get("snake keyboard"))
            display_image(button_x, button_y + 100, game_buttons.get("snake face"))
            display_image(button_x, button_y + 200, game_buttons.get("space invaders keyboard"))
            display_image(button_x, button_y + 300, game_buttons.get("space invaders face"))

            # display demo buttons for face tracking games
            snake_demo_button = pygame.image.load('game/menu/images/buttons/snake demo button.png')
            space_invaders_demo_button = pygame.image.load('game/menu/images/buttons/space invaders demo button.png')
            display_image(200, 680, snake_demo_button)
            display_image(550, 680, space_invaders_demo_button)

            pygame.display.update()
            clock.tick(60)

            # event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                # check if mouse clicked the buttons
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()

                    # get top left coordinates for each button to generate equivalent rect
                    snake_keyboard_button_top_left = get_button_rect_values(button_x, button_y,
                                                                            game_buttons.get("snake keyboard"))
                    snake_face_button_top_left = get_button_rect_values(button_x, button_y + 100,
                                                                        game_buttons.get("snake face"))
                    space_invaders_keyboard_button_top_left = get_button_rect_values(button_x, button_y + 200,
                                                                                     game_buttons.get(
                                                                                         "space invaders keyboard"))
                    space_invaders_face_button_top_left = get_button_rect_values(button_x, button_y + 300,
                                                                                 game_buttons.get(
                                                                                     "space invaders face"))
                    snake_demo_top_left = get_button_rect_values(200, 680, snake_demo_button)
                    space_invaders_demo_top_left = get_button_rect_values(550, 680, space_invaders_demo_button)
                    back_top_left = get_button_rect_values(100, 750, back_button)

                    # first check if the button is greyed out or not
                    if game_buttons.get("snake keyboard") == snake_keyboard_button and snake_keyboard_button.get_rect(
                            topleft=snake_keyboard_button_top_left).collidepoint(mouse_pos):
                        snake_keyboard_game_menu()
                    elif game_buttons.get("snake face") == snake_face_button and snake_face_button.get_rect(
                            topleft=snake_face_button_top_left).collidepoint(mouse_pos):
                        snake_face_game_menu()
                    elif game_buttons.get("space invaders keyboard") == space_invaders_keyboard_button and \
                            space_invaders_keyboard_button.get_rect(topleft=space_invaders_keyboard_button_top_left) \
                                    .collidepoint(mouse_pos):
                        space_invaders_keyboard_game_menu()
                    elif game_buttons.get(
                            "space invaders face") == space_invaders_face_button and space_invaders_face_button.get_rect(
                        topleft=space_invaders_face_button_top_left).collidepoint(mouse_pos):
                        space_invaders_face_game_menu()

                    elif snake_demo_button.get_rect(topleft=snake_demo_top_left).collidepoint(mouse_pos):
                        game_demo_page('game/menu/videos/snake game demo.mp4')
                    elif space_invaders_demo_button.get_rect(topleft=space_invaders_demo_top_left).collidepoint(
                            mouse_pos):
                        game_demo_page('game/menu/videos/Space Invaders demo.mp4')
                    elif back_button.get_rect(topleft=back_top_left).collidepoint(mouse_pos):
                        background_questionnaire_page()


    def snake_keyboard_game():
        import game.snake.snake_keyboard_controlled_game as game
        game.run_game(snake_game_result_metrics, file_name)


    def snake_face_game():
        import game.snake.snake_face_tracking_game_svr as game
        game.run_game(snake_game_result_metrics, file_name)


    def space_invaders_keyboard_game():
        import game.space_invaders.space_invaders_keyboard_controlled_game as game
        game.run_game(space_invaders_result_metrics, file_name)


    def space_invaders_face_game():
        import game.space_invaders.space_invaders_face_tracking_game_svr as game
        game.run_game(space_invaders_result_metrics, file_name)


    def end_of_games_page(start):
        clock = pygame.time.Clock()
        while time.time() - start < 5:
            display.fill(background_colour)
            pygame.display.set_caption("End of User Study")

            text = pygame.image.load('game/menu/images/text/end game message.png')
            display_image(400, 300, text)

            pygame.display.update()
            clock.tick(60)


    def game_menu(text: Surface, game_type: str):
        clock = pygame.time.Clock()

        while True:
            display.fill(background_colour)
            pygame.display.set_caption("Keyboard-Controlled Snake Game Menu")
            # load images
            start_button = pygame.image.load('game/menu/images/buttons/start.png')
            back_button = pygame.image.load('game/menu/images/buttons/back.png')

            text_scale = (text.get_width() // 1.7, text.get_height() // 1.7)
            game_text = pygame.transform.scale(text, text_scale)

            # display text and buttons
            display_image(400, 300, game_text)
            display_image(400, 600, start_button)
            display_image(100, 700, back_button)

            pygame.display.update()
            clock.tick(60)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()

                    # get rects for buttons on display
                    start_top_left = get_button_rect_values(400, 600, start_button)
                    back_top_left = get_button_rect_values(100, 700, back_button)

                    if start_button.get_rect(topleft=start_top_left).collidepoint(mouse_pos):
                        print("Start button clicked")
                        if game_type == "snake keyboard":
                            snake_keyboard_game()
                            reset_menu_size()
                            increment_current_game_idx()
                            snake_keyboard_questionnaire_page()
                        elif game_type == "snake face":
                            display_loading_screen(pygame.image.load('game/menu/images/text/snake loading.png'))
                            snake_face_game()
                            reset_menu_size()
                            increment_current_game_idx()
                            snake_face_questionnaire_page()
                        elif game_type == "space invaders keyboard":
                            space_invaders_keyboard_game()
                            reset_menu_size()
                            increment_current_game_idx()
                            space_invaders_keyboard_questionnaire_page()
                        elif game_type == "space invaders face":
                            display_loading_screen(
                                pygame.image.load('game/menu/images/text/space invaders loading.png'))
                            space_invaders_face_game()
                            reset_menu_size()
                            increment_current_game_idx()
                            space_invaders_face_questionnaire_page()
                        else:
                            print("Invalid game type: " + game_type)
                        reset_menu_size()
                        # increment_current_game_idx()
                        main_menu()
                    elif back_button.get_rect(topleft=back_top_left).collidepoint(mouse_pos):
                        main_menu()


    def increment_current_game_idx():
        global current_game_idx
        current_game_idx += 1
        if current_game_idx > 4:
            current_game_idx = 0
        print("Current Game Index: " + str(current_game_idx))
        return current_game_idx


    def reset_menu_size():
        # to ensure that the menu dimensions stay the same after each game
        global display
        display = pygame.display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT))


    def snake_keyboard_game_menu():
        game_text_unscaled = pygame.image.load('game/menu/images/text/snake keyboard text.png')
        game_type = "snake keyboard"
        game_menu(game_text_unscaled, game_type)


    def snake_face_game_menu():
        game_text_unscaled = pygame.image.load('game/menu/images/text/snake face text.png')
        game_type = "snake face"
        game_menu(game_text_unscaled, game_type)


    def space_invaders_keyboard_game_menu():
        game_text_unscaled = pygame.image.load('game/menu/images/text/space invaders keyboard text.png')
        game_type = "space invaders keyboard"
        game_menu(game_text_unscaled, game_type)


    def space_invaders_face_game_menu():
        game_text_unscaled = pygame.image.load('game/menu/images/text/space invaders face text.png')
        game_type = "space invaders face"
        game_menu(game_text_unscaled, game_type)


    def display_loading_screen(text: Surface):
        display.fill(background_colour)
        display_image(400, 300, text)
        pygame.display.flip()


    def resize_video_output(frame, scale):  # scale given as decimal e.g. 0.75
        height = int(frame.shape[0] * scale)
        width = int(frame.shape[1] * scale)
        new_dimension = (width, height)
        return cv2.resize(frame, new_dimension, interpolation=cv2.INTER_AREA)


    def background_questionnaire_page():
        clock = pygame.time.Clock()
        background_title_original = pygame.image.load('game/menu/images/text/background questionnaire title.png')
        # scale down menu title
        title_scale = (background_title_original.get_width() // 1.3, background_title_original.get_height() // 1.3)
        background_title = pygame.transform.scale(background_title_original, title_scale)

        questionnaire_button_large = pygame.transform.scale(questionnaire_button, (
        questionnaire_button.get_width() * 1.2, questionnaire_button.get_height() * 1.2))

        next_button_unscaled = pygame.image.load('game/menu/images/buttons/next button.png')
        new_scale = (next_button_unscaled.get_width() * 1.3, next_button_unscaled.get_height() * 1.3)
        next_button = pygame.transform.scale(next_button_unscaled, new_scale)

        text = pygame.image.load('game/menu/images/text/background questionnaire text.png')
        text = pygame.transform.scale(text, (text.get_width() // 1.8, text.get_height() // 1.8))

        qr_code = pygame.image.load('game/menu/images/QR_codes/QRCode for Background Questionnaire.png')
        qr_code = pygame.transform.scale(qr_code, (qr_code.get_width() // 7, qr_code.get_height() // 7))

        font = pygame.font.SysFont("Comic Sans", 30, bold=True)
        identifier = font.render("Your unique id is: " + unique_id, True, (255, 128, 0))

        while True:
            display.fill(background_colour)
            display_image(650, 720, next_button)
            display_image(display.get_width() // 2, 100, background_title)
            display_image(400, 640, questionnaire_button_large)
            display_image(400, 400, text)
            display_image(150, 700, qr_code)

            display.blit(identifier, (250, 140))
            pygame.display.update()
            clock.tick(60)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    next_top_left = get_button_rect_values(650, 720, next_button)
                    questionnaire_top_left = get_button_rect_values(400, 640, questionnaire_button)
                    if questionnaire_button.get_rect(topleft=questionnaire_top_left).collidepoint(mouse_pos):
                        webbrowser.open('https://forms.office.com/e/pgNdH75P6n')  # open background questionnaire
                    elif next_button.get_rect(topleft=next_top_left).collidepoint(mouse_pos):
                        main_menu()  # go to main menu if next button pressed


    def snake_keyboard_questionnaire_page():
        text = pygame.image.load('game/menu/images/text/snake keyboard questionnaire text.png')
        qr_code = pygame.image.load(
            'game/menu/images/QR_codes/QRCode for Keyboard-Controlled Snake Game Questionnaire.png')
        link = 'https://forms.office.com/e/EirHSjkmRB'
        game_questionnaire_page(text, qr_code, link)


    def snake_face_questionnaire_page():
        text = pygame.image.load('game/menu/images/text/snake face questionnaire text.png')
        qr_code = pygame.image.load(
            'game/menu/images/QR_codes/QRCode for Face-Tracking Snake Game Questionnaire .png')
        link = 'https://forms.office.com/e/e2HPAHueeE'
        game_questionnaire_page(text, qr_code, link)


    def space_invaders_keyboard_questionnaire_page():
        text = pygame.image.load('game/menu/images/text/space invaders keyboard questionnaire text.png')
        qr_code = pygame.image.load(
            'game/menu/images/QR_codes/QRCode for Keyboard-Controlled Space Invaders Game Questionnaire .png')
        link = 'https://forms.office.com/e/3f9Z1UEyMy'
        game_questionnaire_page(text, qr_code, link)


    def space_invaders_face_questionnaire_page():
        text = pygame.image.load('game/menu/images/text/space invaders face questionnaire text.png')
        qr_code = pygame.image.load(
            'game/menu/images/QR_codes/QRCode for Face-Tracking Space Invaders Game Questionnaire .png')
        link = 'https://forms.office.com/e/Sw3Lh6JxEj'
        game_questionnaire_page(text, qr_code, link)


    def game_questionnaire_page(text, qr_code, link):
        clock = pygame.time.Clock()
        next_button = pygame.image.load('game/menu/images/buttons/next button.png')
        text = pygame.transform.scale(text, (text.get_width() // 1.8, text.get_height() // 1.8))
        qr_code = pygame.transform.scale(qr_code, (qr_code.get_width() // 7, qr_code.get_height() // 7))

        font = pygame.font.SysFont("Comic Sans", 50, bold=True)
        identifier = font.render("Your unique id is: " + unique_id, True, (255, 128, 0))

        while True:
            display.fill(background_colour)
            display_image(650, 700, next_button)
            display_image(400, 400, text)
            display_image(150, 700, qr_code)
            display_image(400, 640, questionnaire_button)
            display.blit(identifier, (160, 85))
            pygame.display.update()
            clock.tick(60)

            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    next_top_left = get_button_rect_values(650, 700, next_button)
                    questionnaire_top_left = get_button_rect_values(400, 600, questionnaire_button)
                    if questionnaire_button.get_rect(topleft=questionnaire_top_left).collidepoint(mouse_pos):
                        webbrowser.open(link)  # open questionnaire
                    elif next_button.get_rect(topleft=next_top_left).collidepoint(mouse_pos):
                        main_menu()  # go to main menu if next button pressed


    def game_demo_page(demo):
        # for showing demo videos of the face tracking games
        display.fill(background_colour)
        # load and display back button
        back_button = pygame.image.load('game/menu/images/buttons/back.png')
        display_image(100, 700, back_button)

        cap = cv2.VideoCapture(demo)  # use opencv to play the demo videos
        ret, frame = cap.read()
        frame = resize_video_output(frame, 0.5)  # scale down the video
        shape = frame.shape[1::-1]  # video shape to pass to pygame
        clock = pygame.time.Clock()
        while True:
            clock.tick(60)
            ret, frame = cap.read()
            if ret:
                frame = resize_video_output(frame, 0.5)
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        main_menu()
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        mouse_pos = pygame.mouse.get_pos()
                        back_top_left = get_button_rect_values(100, 700, back_button)
                        if back_button.get_rect(topleft=back_top_left).collidepoint(mouse_pos):
                            main_menu()  # go back to main menu if back button pressed
            else:
                break
            display.blit(pygame.image.frombuffer(frame.tobytes(), shape, "BGR"), (0, 0))
            pygame.display.update()
        main_menu()


    '''def initialise_test_results_file(unique_id_file_path):
        # read a unique id from the text file
        with open(unique_id_file_path, 'r') as file:
            lines = file.readlines()
            first_line = lines[0].strip()  # Remove leading and trailing whitespace

        # Read the remaining lines into memory
        with open(unique_id_file_path, 'r') as file:
            lines = file.readlines()[1:]  # Read all lines except the first one

        # Write the remaining lines back to the text file
        with open(unique_id_file_path, 'w') as file:
            file.writelines(lines)

        test_file_path = 'user_tests/test_data/' + first_line + '.txt'
        with open(test_file_path, 'w') as file:
            # Write the content to the file
            file.write(first_line)
            
        return first_line'''

    # initialise_test_results_file('user_tests/data/unused_unique_ids2.txt')
    # background_questionnaire_page()
    # snake_keyboard_game()
    # space_invaders_keyboard_game()
    # snake_face_game()
    space_invaders_face_game()

