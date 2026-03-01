"""
Конфигурация приложения
"""

import os

# Базовые пути
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
SHADERS_DIR = os.path.join(ASSETS_DIR, "shaders")
SCENES_DIR = os.path.join(ASSETS_DIR, "scenes")

# Настройки окна
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 800
WINDOW_TITLE = "Steam Deck Multimedia"
TARGET_FPS = 60
FULLSCREEN_DEFAULT = True

# Настройки контроллера Steam Deck
# Маппинг кнопок (SDL/pygame)
class ControllerButtons:
    """Маппинг кнопок Steam Deck контроллера"""
    A = 0        # Нижняя кнопка
    B = 1        # Правая кнопка
    X = 2        # Левая кнопка
    Y = 3        # Верхняя кнопка
    L1 = 4       # Левый бампер
    R1 = 5       # Правый бампер
    SELECT = 6   # View/Select
    START = 7    # Menu/Start (Options)
    HOME = 8     # Steam кнопка
    L3 = 9       # Нажатие левого стика
    R3 = 10      # Нажатие правого стика

    # D-Pad обрабатывается через HAT
    DPAD_UP = "hat_up"
    DPAD_DOWN = "hat_down"
    DPAD_LEFT = "hat_left"
    DPAD_RIGHT = "hat_right"


class ControllerAxes:
    """Маппинг осей контроллера"""
    LEFT_X = 0
    LEFT_Y = 1
    RIGHT_X = 2
    RIGHT_Y = 3
    L2 = 4       # Левый триггер
    R2 = 5       # Правый триггер


# Настройки модификаторов
MODIFIER_HOLD_TIME = 0.15  # Время в секундах для регистрации зажатия

# Настройки анимаций
DEFAULT_ANIMATION_DURATION = 1.0
MAX_CONCURRENT_ANIMATIONS = 100

# Настройки 3D
PLANE_SIZE = 10.0
CAMERA_DISTANCE = 5.0

