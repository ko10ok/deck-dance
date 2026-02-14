"""
Анимация расходящегося круга с затуханием
"""

from typing import Tuple, Dict, Any
from src.animations.base_animation import BaseAnimation
from src.core.renderer import Renderer


class ExpandingCircleAnimation(BaseAnimation):
    """Анимация расходящегося круга (кольца) с затуханием"""

    def __init__(
        self,
        center: Tuple[float, float],
        color: Tuple[float, float, float, float] = (1.0, 1.0, 1.0, 1.0),
        duration: float = 1.0,
        max_radius: float = 150.0,
        ring_width: float = 0.15,
        **kwargs
    ):
        super().__init__(center, duration, **kwargs)
        self.color = color
        self.max_radius = max_radius
        self.ring_width = ring_width

        # Текущие значения
        self.current_radius = 0.0
        self.current_alpha = 1.0

    def _update(self, dt: float):
        """Обновление радиуса и прозрачности"""
        # Easing функция для плавного расширения
        eased_progress = self._ease_out_quad(self.progress)

        # Радиус растёт от 0 до max_radius
        self.current_radius = eased_progress * self.max_radius

        # Прозрачность уменьшается к концу анимации
        # Начинаем затухание после 50% прогресса
        fade_start = 0.3
        if self.progress > fade_start:
            fade_progress = (self.progress - fade_start) / (1.0 - fade_start)
            self.current_alpha = 1.0 - self._ease_in_quad(fade_progress)
        else:
            self.current_alpha = 1.0

    def _ease_out_quad(self, t: float) -> float:
        """Easing функция - замедление в конце"""
        return 1 - (1 - t) * (1 - t)

    def _ease_in_quad(self, t: float) -> float:
        """Easing функция - ускорение"""
        return t * t

    def render(self, renderer: Renderer):
        """Отрисовка круга"""
        if self.finished or self.current_alpha <= 0.01:
            return

        renderer.render_circle(
            center=self.center,
            radius=self.current_radius,
            alpha=self.current_alpha,
            color=self.color,
            ring_width=self.ring_width
        )

    @classmethod
    def get_config_schema(cls) -> Dict[str, Any]:
        """Схема конфигурации для редактора"""
        schema = super().get_config_schema()
        schema.update({
            "color": {"type": "color", "default": (1.0, 1.0, 1.0, 1.0)},
            "max_radius": {"type": "float", "default": 150.0, "min": 10.0, "max": 500.0},
            "ring_width": {"type": "float", "default": 0.15, "min": 0.01, "max": 0.5},
        })
        return schema

