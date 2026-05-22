from pathlib import Path

import pygame

# Не стоит здесь что-то менять, хоть этот раздел и находится в /blockcraft, о котором я говорил в README
# Здесь функция для загрузки изображений и отрисовки текста в UI

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def _resolve(path):
    """Преобразует относительный путь в абсолютный относительно корня проекта"""
    p = Path(path)
    if p.is_absolute():
        return p
    return PROJECT_ROOT / p


def load_image(path, size=None):
    """Загружает изображения по указанному пути"""
    try:
        image = pygame.image.load(str(_resolve(path)))
        if size:
            image = pygame.transform.scale(image, size)
        return image.convert_alpha()
    except Exception:
        surface = pygame.Surface((50, 50))
        surface.fill((255, 0, 255))
        return surface


def draw_text(surface, text, pos, font_size=24, color=(255, 255, 255)):
    """Отрисовка текста в UI"""
    try:
        font = pygame.font.SysFont(None, font_size)
        text_surface = font.render(text, True, color)
        surface.blit(text_surface, pos)
    except Exception:
        pass
