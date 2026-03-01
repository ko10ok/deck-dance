"""
Анимация отскакивающей линии в расширяющемся квадрате.
Концы линии движутся независимо и отскакиваются от границ.
"""

import numpy as np
import math
from typing import Tuple, Dict, Any
from numba import jit
from src.animations.base_animation import BaseAnimation
from src.core.renderer import Renderer


@jit(nopython=True, cache=True)
def update_point_physics(
    pos: np.ndarray,
    velocity: np.ndarray,
    box_size: float,
    center_x: float,
    center_y: float,
    dt: float
) -> None:
    """
    JIT-компилированное обновление физики одной точки.
    Точка отскакивает от границ виртуального квадрата.
    """
    # Обновляем позицию
    pos[0] += velocity[0] * dt
    pos[1] += velocity[1] * dt

    half_box = box_size / 2.0

    # Границы относительно центра
    min_x = center_x - half_box
    max_x = center_x + half_box
    min_y = center_y - half_box
    max_y = center_y + half_box

    # Отскок от границ
    if pos[0] <= min_x:
        pos[0] = min_x
        velocity[0] = abs(velocity[0])
    elif pos[0] >= max_x:
        pos[0] = max_x
        velocity[0] = -abs(velocity[0])

    if pos[1] <= min_y:
        pos[1] = min_y
        velocity[1] = abs(velocity[1])
    elif pos[1] >= max_y:
        pos[1] = max_y
        velocity[1] = -abs(velocity[1])


class BouncingLineAnimation(BaseAnimation):
    """
    Анимация линии с независимыми концами в расширяющемся/сужающемся квадрате.

    Каждый конец линии движется независимо и отскакивает от границ квадрата.
    Длина линии меняется динамически в зависимости от положения концов.
    """

    def __init__(
        self,
        center: Tuple[float, float],
        color: Tuple[float, float, float, float] = (0.0, 1.0, 1.0, 1.0),
        duration: float = 3.0,
        initial_box_size: float = 20.0,
        max_box_size: float = 300.0,
        speed: float = 200.0,
        expand: bool = True,
        line_style: str = "solid",  # "solid" или "dotted"
        **kwargs
    ):
        super().__init__(center, duration, **kwargs)
        self.color = np.array(color, dtype=np.float32)
        self.initial_box_size = initial_box_size
        self.max_box_size = max_box_size
        self.speed = speed
        self.expand = expand
        self.line_style = line_style

        # Текущий размер квадрата
        if expand:
            self.current_box_size = initial_box_size
        else:
            self.current_box_size = max_box_size

        # Два конца линии - абсолютные координаты
        # Стартовые позиции рандомизируются в пределах текущего бокса
        half_box = self.current_box_size / 2.0
        self.point1 = np.array([
            center[0] + np.random.uniform(-half_box, half_box),
            center[1] + np.random.uniform(-half_box, half_box)
        ], dtype=np.float32)
        self.point2 = np.array([
            center[0] + np.random.uniform(-half_box, half_box),
            center[1] + np.random.uniform(-half_box, half_box)
        ], dtype=np.float32)

        # Независимые скорости для каждого конца
        angle1 = np.random.uniform(0, 2 * math.pi)
        angle2 = np.random.uniform(0, 2 * math.pi)

        self.velocity1 = np.array([
            math.cos(angle1) * speed,
            math.sin(angle1) * speed
        ], dtype=np.float32)

        self.velocity2 = np.array([
            math.cos(angle2) * speed,
            math.sin(angle2) * speed
        ], dtype=np.float32)

    def _update(self, dt: float):
        """Обновление анимации"""
        # Изменяем размер квадрата
        if self.expand:
            self.current_box_size = self.initial_box_size + \
                (self.max_box_size - self.initial_box_size) * self.progress
        else:
            self.current_box_size = self.max_box_size - \
                (self.max_box_size - self.initial_box_size) * self.progress

        # Обновляем физику каждого конца независимо
        update_point_physics(
            self.point1,
            self.velocity1,
            self.current_box_size,
            float(self.center[0]),
            float(self.center[1]),
            dt
        )

        update_point_physics(
            self.point2,
            self.velocity2,
            self.current_box_size,
            float(self.center[0]),
            float(self.center[1]),
            dt
        )

        # Завершение
        if self.elapsed >= self.duration:
            self.finished = True

    def render(self, renderer: Renderer):
        """Отрисовка цельной линии между двумя точками с использованием instanced rendering"""
        if self.finished:
            return

        x1, y1 = float(self.point1[0]), float(self.point1[1])
        x2, y2 = float(self.point2[0]), float(self.point2[1])

        # Прозрачность уменьшается к концу
        alpha = (1.0 - self.progress * 0.5) * float(self.color[3])

        # Вычисляем длину линии и количество сегментов
        line_length = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

        if self.line_style == "solid":
            # Сплошная линия - меньше сегментов для оптимизации
            num_segments = max(8, int(line_length / 5))
            size = 3.0
        else:
            # Точечная линия - меньше точек, разреженные
            num_segments = max(5, int(line_length / 15))
            size = 4.0  # базовый размер

        # Предвычисляем все позиции и параметры за раз
        t_values = np.linspace(0, 1, num_segments, dtype=np.float32)

        centers = np.zeros((num_segments, 2), dtype=np.float32)
        centers[:, 0] = x1 + (x2 - x1) * t_values
        centers[:, 1] = y1 + (y2 - y1) * t_values

        if self.line_style == "solid":
            radii = np.full(num_segments, size, dtype=np.float32)
        else:
            # Размер точки больше на концах
            radii = (4.0 + 1.5 * (1.0 - np.abs(t_values - 0.5) * 2)).astype(np.float32)

        # Цвета с альфой
        colors = np.zeros((num_segments, 4), dtype=np.float32)
        colors[:, 0] = self.color[0]
        colors[:, 1] = self.color[1]
        colors[:, 2] = self.color[2]
        colors[:, 3] = alpha

        # Один draw call для всех сегментов линии!
        renderer.render_circles_instanced(centers, radii, colors, ring_width=0.5)

    @classmethod
    def get_config_schema(cls) -> Dict[str, Any]:
        """Схема конфигурации для редактора"""
        schema = super().get_config_schema()
        schema.update({
            "color": {"type": "color", "default": (0.0, 1.0, 1.0, 1.0)},
            "initial_box_size": {"type": "float", "default": 20.0, "min": 5.0, "max": 100.0},
            "max_box_size": {"type": "float", "default": 300.0, "min": 50.0, "max": 800.0},
            "speed": {"type": "float", "default": 200.0, "min": 50.0, "max": 500.0},
            "expand": {"type": "bool", "default": True},
            "line_style": {"type": "string", "default": "solid", "options": ["solid", "dotted"]},
        })
        return schema












