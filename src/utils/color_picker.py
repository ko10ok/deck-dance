"""
Помощник для выбора цвета на основе ввода
"""

import math
from typing import Tuple, Optional, List
import pygame
from src.utils.color_utils import hsv_to_rgb


class ColorPicker:
    """
    Статический класс-помощник для выбора цвета.
    Конвертирует ввод (клавиатура/джойстик) в цвет.
    """

    # Маппинг клавиш 1-9 на углы цветового круга (hue)
    # Расположение как на numpad: 7-8-9 сверху, 1-2-3 снизу
    KEY_TO_HUE = {
        pygame.K_1: 225,   # Синий
        pygame.K_2: 270,   # Фиолетовый
        pygame.K_3: 315,   # Розовый
        pygame.K_4: 180,   # Голубой
        pygame.K_5: 0,     # Красный
        pygame.K_6: 30,    # Оранжево-красный
        pygame.K_7: 135,   # Зелёный
        pygame.K_8: 90,    # Жёлто-зелёный
        pygame.K_9: 45,    # Оранжевый
    }

    # Минимальное отклонение стика для регистрации
    STICK_DEADZONE = 0.3

    @staticmethod
    def from_stick(stick: Tuple[float, float]) -> Optional[Tuple[float, Tuple[float, float, float, float]]]:
        """
        Получить цвет на основе положения стика.

        Args:
            stick: Координаты стика (x, y), каждая от -1 до 1

        Returns:
            Кортеж (hue, (r, g, b, a)) или None если стик в мёртвой зоне
        """
        stick_x, stick_y = stick
        magnitude = math.sqrt(stick_x * stick_x + stick_y * stick_y)

        if magnitude <= ColorPicker.STICK_DEADZONE:
            return None

        # Угол стика определяет оттенок (hue)
        angle = math.atan2(stick_y, stick_x)
        # Конвертируем из радиан (-π to π) в градусы (0-360)
        hue = (math.degrees(angle) + 360) % 360

        # Конвертируем HSV в RGB (максимальная насыщенность)
        r, g, b = hsv_to_rgb(hue)

        return (hue, (r, g, b, 1.0))

    @staticmethod
    def from_keys(pressed_keys: List[int]) -> Optional[Tuple[float, Tuple[float, float, float, float]]]:
        """
        Получить цвет на основе нажатых клавиш.

        Args:
            pressed_keys: Список кодов нажатых клавиш

        Returns:
            Кортеж (hue, (r, g, b, a)) или None если ни одна цветовая клавиша не нажата
        """
        for key in pressed_keys:
            if key in ColorPicker.KEY_TO_HUE:
                hue = ColorPicker.KEY_TO_HUE[key]
                r, g, b = hsv_to_rgb(hue)
                return (hue, (r, g, b, 1.0))

        return None

    @staticmethod
    def get_color(
        pressed_keys: List[int],
        stick: Tuple[float, float] = (0.0, 0.0)
    ) -> Optional[Tuple[float, Tuple[float, float, float, float]]]:
        """
        Получить цвет на основе любого ввода.
        Приоритет: клавиатура > стик.

        Args:
            pressed_keys: Список кодов нажатых клавиш
            stick: Координаты стика (x, y), каждая от -1 до 1

        Returns:
            Кортеж (hue, (r, g, b, a)) или None если ввод не содержит выбора цвета
        """
        # Сначала проверяем клавиатуру
        result = ColorPicker.from_keys(pressed_keys)
        if result:
            return result

        # Затем проверяем стик
        return ColorPicker.from_stick(stick)

    @staticmethod
    def get_available_keys() -> List[int]:
        """Получить список клавиш для выбора цвета"""
        return list(ColorPicker.KEY_TO_HUE.keys())



