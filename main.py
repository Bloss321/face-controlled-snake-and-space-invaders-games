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
    main_menu_title_original = pygame.image.load('game/menu/images/text/main menu.png')
    # scale down menu title
    scale = (main_menu_title_original.get_width() // 1.5, main_menu_title_original.get_height() // 1.5)
    main_menu_title = pygame.transform.scale(main_menu_title_original, scale)
    # load button images for games
    snake_keyboard_button = pygame.image.load('game/menu/images/snake keyboard.png')
    snake_face_button = pygame.image.load('game/menu/images/snake face.png')
    space_invaders_keyboard_button = pygame.image.load('game/menu/images/space invaders keyboard.png')
    space_invaders_face_button = pygame.image.load('game/menu/images/space invaders face.png')

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


    def get_button_rect_values(x_pos, y_pos, image: Surface):
        rect = image.get_rect()
        x = x_pos - rect.width / 2
        y = y_pos - rect.height / 2
        return x, y


    def display_image(x_pos, y_pos, button_image: Surface):
        top_left = get_button_rect_values(x_pos, y_pos, button_image)
        display.blit(button_image, top_left)


    def main_menu():
        clock = pygame.time.Clock()

        while True:
            display.fill(background_colour)
            display_image(DISPLAY_WIDTH // 2, 150, main_menu_title)

            # Draw buttons
            button_width = 200
            button_height = 50
            button_x = DISPLAY_WIDTH // 2  # 400
            button_y = 300

            # display menu buttons for games
            display_image(button_x, button_y, snake_keyboard_button)
            display_image(button_x, button_y + 100, snake_face_button)
            display_image(button_x, button_y + 200, space_invaders_keyboard_button)
            display_image(button_x, button_y + 300, space_invaders_face_button)

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
                    snake_keyboard_button_top_left = get_button_rect_values(button_x, button_y, snake_keyboard_button)
                    snake_face_button_top_left = get_button_rect_values(button_x, button_y + 100, snake_face_button)
                    space_invaders_keyboard_button_top_left = get_button_rect_values(button_x, button_y + 200,
                                                                                     space_invaders_keyboard_button)
                    space_invaders_face_button_top_left = get_button_rect_values(button_x, button_y + 300,
                                                                                 space_invaders_face_button)

                    if snake_keyboard_button.get_rect(topleft=snake_keyboard_button_top_left).collidepoint(mouse_pos):
                        print("Snake Keyboard Game button clicked - WORKING")
                        snake_keyboard_game_menu()
                    elif snake_face_button.get_rect(topleft=snake_face_button_top_left).collidepoint(mouse_pos):
                        print("Snake Face Tracking Game button clicked")
                        snake_face_game_menu()
                    elif space_invaders_keyboard_button.get_rect(
                            topleft=space_invaders_keyboard_button_top_left).collidepoint(
                        mouse_pos):
                        print("Space Invaders keyboard button clicked")
                        space_invaders_keyboard_game_menu()
                    elif space_invaders_face_button.get_rect(topleft=space_invaders_face_button_top_left).collidepoint(
                            mouse_pos):
                        print("Space Invaders Face Tracking button clicked")
                        space_invaders_face_game_menu()
                        # this should only run after the last game has been played?
                        # pygame.quit()
                        # sys.exit()


    def snake_keyboard_game():
        import game.snake.simple.simple_snake_hand_controlled as simple_hand
        simple_hand.run_game(time.time(), simple_game_result_metrics, file_name)


    def snake_face_game():
        import game.snake.simple.mp_simple_snake_remove_lagging as mp_simple_face
        mp_simple_face.run_game(time.time(), simple_game_result_metrics, file_name)


    def space_invaders_keyboard_game():
        import game.space_invaders.hand_controlled_game as hand_space_invaders
        hand_space_invaders.run_game()


    def space_invaders_face_game():
        import game.space_invaders.face_tracking_game as face_tracking_space_invaders
        face_tracking_space_invaders.run_game()


    def game_menu(text: Surface, game_type: str):
        clock = pygame.time.Clock()

        while True:
            display.fill(background_colour)
            pygame.display.set_caption("Keyboard-Controlled Snake Game Menu")
            # load images
            start_button = pygame.image.load('game/menu/images/start.png')
            back_button = pygame.image.load('game/menu/images/back.png')

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
                    elif back_button.get_rect(topleft=back_top_left).collidepoint(mouse_pos):
                        print("Back button clicked")
                        main_menu()


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
