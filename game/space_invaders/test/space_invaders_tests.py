import pygame
import pytest
from unittest.mock import Mock, patch

from game.space_invaders.alien import Alien
from game.space_invaders.player import Player

display_width = 800
display_height = 600


@pytest.fixture(autouse=True)
def mock_pygame_image_load(monkeypatch):
    mock_image = Mock()
    monkeypatch.setattr(pygame.image, 'load', lambda x: mock_image)


@pytest.fixture()
def display():
    return pygame.display.set_mode((display_width, display_height))


@pytest.fixture()
def player():
    return Player()


@pytest.fixture()
def alien():
    return Alien()

@pytest.fixture()
def aliens():
    return [Alien() for _ in range(6)]


def test_initial_player_position(player):
    assert player.x_pos == 400
    assert player.y_pos == 500


def test_move_player_left(player):
    initial_x = player.convert_to_rect().x
    player.x_change = -5
    player.move()
    assert player.convert_to_rect().x == initial_x + player.x_change == 395


def test_move_player_right(player):
    initial_x = player.convert_to_rect().x
    player.x_change = 5
    player.move()
    assert player.convert_to_rect().x == initial_x + player.x_change == 405  # 400 + 5 = 405


def test_generate_player(player):
    mock_display = Mock()
    mock_display.blit = Mock()
    player.generate(mock_display)
    mock_display.blit.assert_called_once_with(player.image, (player.x_pos, player.y_pos))


