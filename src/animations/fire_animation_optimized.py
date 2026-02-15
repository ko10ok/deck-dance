"""
Оптимизированная анимация огня - частицы с instanced rendering
"""

import numpy as np
import math
from typing import Tuple, Dict, Any
from src.animations.base_animation import BaseAnimation
from src.core.renderer import Renderer


class FireAnimationOptimized(BaseAnimation):
    """
    Оптимизированная анимация огня с NumPy и instanced rendering.

    Оптимизации:
    - Все частицы хранятся в numpy массивах (нет Python объектов)
    - Векторизованное обновление позиций (без циклов по частицам)
    - Instanced rendering - все частицы за один draw call
    - Пул частиц - нет аллокаций во время работы
    """

    def __init__(
        self,
        center: Tuple[float, float],
        color: Tuple[float, float, float, float] = (0.3, 1.0, 0.4, 1.0),
        duration: float = 2.0,
        particle_count: int = 30,
        spread: float = 50.0,
        initial_speed: float = 120.0,
        gravity: Tuple[float, float] = (0.0, -100.0),
        **kwargs
    ):
        super().__init__(center, duration, **kwargs)
        self.base_color = np.array(color, dtype=np.float32)
        self.particle_count = particle_count
        self.spread = spread
        self.initial_speed = initial_speed
        self.gravity = np.array(gravity, dtype=np.float32)

        # Пул частиц - все данные в numpy массивах (фиксированный размер)
        self.max_particles = particle_count

        # Позиции (x, y)
        self.positions = np.zeros((self.max_particles, 2), dtype=np.float32)
        # Скорости (vx, vy)
        self.velocities = np.zeros((self.max_particles, 2), dtype=np.float32)
        # Размеры частиц
        self.sizes = np.zeros(self.max_particles, dtype=np.float32)
        # Время жизни (текущее, максимальное)
        self.lifetimes = np.zeros(self.max_particles, dtype=np.float32)
        self.max_lifetimes = np.zeros(self.max_particles, dtype=np.float32)
        # Флаг активности частицы
        self.active = np.zeros(self.max_particles, dtype=bool)

        # Эмиссия частиц
        self.emit_interval = 0.005
        self.emit_timer = 0.0
        self.particles_emitted = 0
        self.next_particle_idx = 0

        # Кэш для рендеринга (чтобы не создавать каждый кадр)
        self._render_data = None

    def _emit_particle(self):
        """Эмиссия одной частицы в пул"""
        idx = self.next_particle_idx

        # Позиция в центре
        self.positions[idx] = self.center

        # Случайный угол
        angle = np.random.uniform(0, 2 * math.pi)
        speed = self.initial_speed * np.random.uniform(0.7, 1.3)

        self.velocities[idx, 0] = math.cos(angle) * speed
        self.velocities[idx, 1] = math.sin(angle) * speed

        # Случайный размер и время жизни
        self.sizes[idx] = np.random.uniform(5, 20)
        self.lifetimes[idx] = 0.0
        self.max_lifetimes[idx] = np.random.uniform(0.5, 1.2)
        self.active[idx] = True

        self.next_particle_idx = (self.next_particle_idx + 1) % self.max_particles

    def _update(self, dt: float):
        """Векторизованное обновление всех частиц"""
        # Эмиссия новых частиц
        if self.progress < 0.7 and self.particles_emitted < self.particle_count:
            self.emit_timer += dt
            while self.emit_timer >= self.emit_interval and self.particles_emitted < self.particle_count:
                self._emit_particle()
                self.emit_timer -= self.emit_interval
                self.particles_emitted += 1

        # Маска активных частиц
        active_mask = self.active

        if not np.any(active_mask):
            if self.elapsed >= self.duration:
                self.finished = True
            return

        # Векторизованное обновление (работает сразу со всеми активными частицами)
        # Обновляем время жизни
        self.lifetimes[active_mask] += dt

        # Применяем гравитацию к скорости
        self.velocities[active_mask] += self.gravity * dt

        # Обновляем позиции
        self.positions[active_mask] += self.velocities[active_mask] * dt

        # Уменьшаем размер
        self.sizes[active_mask] *= (1.0 - dt * 0.5)

        # Деактивируем мёртвые частицы
        dead_mask = self.lifetimes >= self.max_lifetimes
        self.active[dead_mask] = False

        # Проверяем завершение
        if self.elapsed >= self.duration and not np.any(self.active):
            self.finished = True

    def render(self, renderer: Renderer):
        """Отрисовка частиц - оптимизированная версия"""
        if self.finished:
            return

        active_mask = self.active
        active_count = np.sum(active_mask)

        if active_count == 0:
            return

        # Получаем только активные частицы
        positions = self.positions[active_mask]
        sizes = self.sizes[active_mask]
        lifetimes = self.lifetimes[active_mask]
        max_lifetimes = self.max_lifetimes[active_mask]

        # Вычисляем прогресс для каждой частицы
        progress = np.clip(lifetimes / max_lifetimes, 0, 1)

        # Вычисляем цвета (векторизованно)
        colors = np.zeros((active_count, 4), dtype=np.float32)
        colors[:, 0] = self.base_color[0]  # R
        colors[:, 1] = self.base_color[1] * (1.0 - progress * 0.7)  # G
        colors[:, 2] = self.base_color[2] * (1.0 - progress)  # B
        colors[:, 3] = (1.0 - progress) * self.base_color[3]  # Alpha

        # Фильтруем видимые частицы
        visible_mask = (colors[:, 3] > 0.01) & (sizes > 1)

        if not np.any(visible_mask):
            return

        # Пробуем использовать instanced rendering если доступен
        if hasattr(renderer, 'render_circles_instanced'):
            renderer.render_circles_instanced(
                positions[visible_mask],
                sizes[visible_mask],
                colors[visible_mask],
                ring_width=0.5
            )
        else:
            # Fallback: обычный рендеринг (но всё равно быстрее из-за numpy)
            visible_positions = positions[visible_mask]
            visible_sizes = sizes[visible_mask]
            visible_colors = colors[visible_mask]

            for i in range(len(visible_positions)):
                renderer.render_circle(
                    center=tuple(visible_positions[i]),
                    radius=float(visible_sizes[i]),
                    alpha=float(visible_colors[i, 3]),
                    color=tuple(visible_colors[i]),
                    ring_width=0.5
                )

    @classmethod
    def get_config_schema(cls) -> Dict[str, Any]:
        """Схема конфигурации для редактора"""
        schema = super().get_config_schema()
        schema.update({
            "color": {"type": "color", "default": (0.3, 1.0, 0.4, 1.0)},
            "particle_count": {"type": "int", "default": 30, "min": 5, "max": 500},
            "spread": {"type": "float", "default": 50.0, "min": 10.0, "max": 200.0},
            "initial_speed": {"type": "float", "default": 120.0, "min": 20.0, "max": 300.0},
            "gravity": {"type": "vector2", "default": (0.0, -100.0)},
        })
        return schema



