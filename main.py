import time
import psutil
import pygame
import sys

from pygame import Surface

if __name__ == '__main__':

    pygame.init()

    DISPLAY_WIDTH = 800  # set up display dimensions
    DISPLAY_HEIGHT = 800

    # colours for menu
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    GRAY = (200, 200, 200)
    background_colour = (51, 102, 153)

    display = pygame.display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT))
    pygame.display.set_caption("Start Menu")

    # load menu title image
    main_menu_title_original = pygame.image.load('game/menu/images/text/main menu title.png')
    # scale down menu title
    scale = (main_menu_title_original.get_width() // 1.5, main_menu_title_original.get_height() // 1.5)
    main_menu_title = pygame.transform.scale(main_menu_title_original, scale)
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
    current_game_idx = 3

    file_name = "Test.txt"

    snake_game_result_metrics = {
        "number_of_game_failures": 0,
        "scores_per_game": [],  # number of fruit eaten
    }

    space_invaders_result_metrics = {
        "number_of_game_failures": 0,
        "scores_per_game": [],  # number of aliens hit successfully
        "space_invaders_hit_per_game": [],
        "hits_per_game": []  # number of times player is hit by alien laser per game
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


    def main_menu():
        clock = pygame.time.Clock()

        while True:
            display.fill(background_colour)
            display_image(DISPLAY_WIDTH // 2, 150, main_menu_title)

            # Draw buttons
            button_x = DISPLAY_WIDTH // 2  # 400
            button_y = 300

            game_buttons = load_correct_game_buttons(gameplay_order[current_game_idx])

            # display menu buttons for games
            display_image(button_x, button_y, game_buttons.get("snake keyboard"))
            display_image(button_x, button_y + 100, game_buttons.get("snake face"))
            display_image(button_x, button_y + 200, game_buttons.get("space invaders keyboard"))
            display_image(button_x, button_y + 300, game_buttons.get("space invaders face"))

            pygame.display.update()
            clock.tick(60)

            # Event handling
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
                        # this should only run after the last game has been played?
                        # pygame.quit()
                        # sys.exit()


    def snake_keyboard_game():
        import game.snake.simple.simple_snake_hand_controlled as simple_hand
        simple_hand.run_game(time.time(), snake_game_result_metrics, file_name)


    def snake_face_game():
        import game.snake.simple.mp_simple_snake_remove_lagging as mp_simple_face
        mp_simple_face.run_game(time.time(), snake_game_result_metrics, file_name)


    def space_invaders_keyboard_game():
        import game.space_invaders.hand_controlled_game as hand_space_invaders
        hand_space_invaders.run_game(time.time())


    def space_invaders_face_game():
        import game.space_invaders.face_tracking_game as face_tracking_space_invaders
        face_tracking_space_invaders.run_game(time.time())


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
                    back_top_left = get_button_rect_values(50, 700, back_button)

                    if start_button.get_rect(topleft=start_top_left).collidepoint(mouse_pos):
                        print("Start button clicked")
                        if game_type == "snake keyboard":
                            snake_keyboard_game()
                        elif game_type == "snake face":
                            snake_face_game()
                        elif game_type == "space invaders keyboard":
                            space_invaders_keyboard_game()
                        elif game_type == "space invaders face":
                            space_invaders_face_game()
                        else:
                            print("Invalid game type: " + game_type)
                        reset_menu_size()
                        # increment_current_game_idx()
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


    main_menu()
