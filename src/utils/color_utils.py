"""
Утилиты для работы с цветом
"""

from typing import Tuple


def hsv_to_rgb(h: float, s: float = 1.0, v: float = 1.0) -> Tuple[float, float, float]:
    """
    Конвертация HSV в RGB.

    Args:
        h: Оттенок (hue) 0-360 градусов
        s: Насыщенность (saturation) 0-1
        v: Яркость (value) 0-1

    Returns:
        Кортеж (r, g, b) с значениями 0-1
    """
    h = h % 360
    c = v * s
    x = c * (1 - abs((h / 60) % 2 - 1))
    m = v - c

    if h < 60:
        r, g, b = c, x, 0
    elif h < 120:
        r, g, b = x, c, 0
    elif h < 180:
        r, g, b = 0, c, x
    elif h < 240:
        r, g, b = 0, x, c
    elif h < 300:
        r, g, b = x, 0, c
    else:
        r, g, b = c, 0, x

    return (r + m, g + m, b + m)


def rgb_to_hsv(r: float, g: float, b: float) -> Tuple[float, float, float]:
    """
    Конвертация RGB в HSV.

    Args:
        r: Красный 0-1
        g: Зелёный 0-1
        b: Синий 0-1

    Returns:
        Кортеж (h, s, v) где h 0-360, s и v 0-1
    """
    max_c = max(r, g, b)
    min_c = min(r, g, b)
    delta = max_c - min_c

    # Hue
    if delta == 0:
        h = 0
    elif max_c == r:
        h = 60 * (((g - b) / delta) % 6)
    elif max_c == g:
        h = 60 * (((b - r) / delta) + 2)
    else:
        h = 60 * (((r - g) / delta) + 4)

    # Saturation
    s = 0 if max_c == 0 else delta / max_c

    # Value
    v = max_c

    return (h, s, v)


def hue_to_rgb(h: float) -> Tuple[float, float, float]:
    """
    Конвертация оттенка в RGB с максимальной насыщенностью и яркостью.

    Args:
        h: Оттенок (hue) 0-360 градусов

    Returns:
        Кортеж (r, g, b) с значениями 0-1
    """
    return hsv_to_rgb(h, 1.0, 1.0)

