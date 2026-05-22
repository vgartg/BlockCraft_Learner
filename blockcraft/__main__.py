"""Точка входа: `python -m blockcraft`."""

import sys

import pygame

from mods.my_blocks import BLOCKS
from mods.my_config import GAME_CONFIG
from mods.my_player import PLAYER_CONFIG

from .engine import GameEngine

# Не стоит здесь что-то менять
# Здесь просто создается экземпляр класса игры и происходит её запуск


def main():
    try:
        engine = GameEngine(GAME_CONFIG, BLOCKS, PLAYER_CONFIG)
        engine.run()
    finally:
        pygame.quit()
        sys.exit()


if __name__ == '__main__':
    main()
