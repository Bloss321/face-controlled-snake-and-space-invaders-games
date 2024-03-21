import pygame
from pygame import Surface

countdown_images_unscaled = [
    pygame.image.load('game/countdown/countdown 1.png'),
    pygame.image.load('game/countdown/countdown 2.png'),
    pygame.image.load('game/countdown/countdown 3.png')
]

# scale down images
countdown_images = []
for count_image in countdown_images_unscaled:
    scale = (count_image.get_width() // 2, count_image.get_height() // 2)
    countdown_images.append(pygame.transform.scale(count_image, scale))


def get_count_location(image: Surface, display_width, display_height):
    x_pos = display_width // 2 - (image.get_width() // 2)
    y_pos = display_height // 2 - (image.get_height() // 2)
    return x_pos, y_pos


def start_game_countdown(display: Surface, display_width, display_height):
    for i in range(3):
        display.blit(countdown_images[i], get_count_location(countdown_images[i], display_width, display_height))
        pygame.display.update()
        pygame.time.delay(1000)  # delay for 1 second
