"""
Оптимизированная анимация огня - частицы с instanced rendering и Numba JIT
"""

import numpy as np
import math
from typing import Tuple, Dict, Any
from numba import jit, prange
from src.animations.base_animation import BaseAnimation
from src.core.renderer import Renderer


# ============================================================================
# Numba JIT-компилированные функции для максимальной производительности
# ============================================================================

@jit(nopython=True, cache=True)
def update_particles_physics(
    positions: np.ndarray,
    velocities: np.ndarray,
    sizes: np.ndarray,
    lifetimes: np.ndarray,
    max_lifetimes: np.ndarray,
    active: np.ndarray,
    gravity: np.ndarray,
    dt: float
) -> None:
    """
    JIT-компилированное обновление физики всех частиц.
    Работает в ~10-100 раз быстрее чистого Python.
    """
    n = len(active)
    for i in range(n):
        if active[i]:
            # Обновляем время жизни
            lifetimes[i] += dt

            # Проверяем смерть частицы
            if lifetimes[i] >= max_lifetimes[i]:
                active[i] = False
                continue

            # Применяем гравитацию к скорости
            velocities[i, 0] += gravity[0] * dt
            velocities[i, 1] += gravity[1] * dt

            # Обновляем позицию
            positions[i, 0] += velocities[i, 0] * dt
            positions[i, 1] += velocities[i, 1] * dt

            # Уменьшаем размер
            sizes[i] *= (1.0 - dt * 0.5)


@jit(nopython=True, cache=True)
def compute_particle_colors(
    lifetimes: np.ndarray,
    max_lifetimes: np.ndarray,
    sizes: np.ndarray,
    active: np.ndarray,
    base_color: np.ndarray,
    out_colors: np.ndarray,
    out_visible: np.ndarray
) -> int:
    """
    JIT-компилированное вычисление цветов частиц.
    Возвращает количество видимых частиц.
    """
    visible_count = 0
    n = len(active)

    for i in range(n):
        if active[i]:
            # Прогресс жизни частицы (0 -> 1)
            progress = lifetimes[i] / max_lifetimes[i]
            if progress > 1.0:
                progress = 1.0

            # Вычисляем альфу
            alpha = (1.0 - progress) * base_color[3]

            # Проверяем видимость
            if alpha > 0.01 and sizes[i] > 1.0:
                out_colors[visible_count, 0] = base_color[0]  # R
                out_colors[visible_count, 1] = base_color[1] * (1.0 - progress * 0.7)  # G
                out_colors[visible_count, 2] = base_color[2] * (1.0 - progress)  # B
                out_colors[visible_count, 3] = alpha
                out_visible[visible_count] = i
                visible_count += 1

    return visible_count


@jit(nopython=True, cache=True)
def emit_particles_batch(
    positions: np.ndarray,
    velocities: np.ndarray,
    sizes: np.ndarray,
    lifetimes: np.ndarray,
    max_lifetimes: np.ndarray,
    active: np.ndarray,
    center_x: float,
    center_y: float,
    initial_speed: float,
    start_idx: int,
    count: int,
    max_particles: int,
    # Random values pre-generated (Numba doesn't support all numpy.random)
    random_angles: np.ndarray,
    random_speeds: np.ndarray,
    random_sizes: np.ndarray,
    random_lifetimes: np.ndarray
) -> int:
    """
    JIT-компилированная эмиссия пачки частиц.
    Возвращает новый индекс следующей частицы.
    """
    idx = start_idx
    for i in range(count):
        # Позиция в центре
        positions[idx, 0] = center_x
        positions[idx, 1] = center_y

        # Скорость из предгенерированных случайных значений
        angle = random_angles[i]
        speed = initial_speed * random_speeds[i]
        velocities[idx, 0] = math.cos(angle) * speed
        velocities[idx, 1] = math.sin(angle) * speed

        # Размер и время жизни
        sizes[idx] = random_sizes[i]
        lifetimes[idx] = 0.0
        max_lifetimes[idx] = random_lifetimes[i]
        active[idx] = True

        idx = (idx + 1) % max_particles

    return idx


class FireAnimationOptimized(BaseAnimation):
    """
    Оптимизированная анимация огня с NumPy, Numba JIT и instanced rendering.

    Оптимизации:
    - Все частицы хранятся в numpy массивах (нет Python объектов)
    - Numba JIT-компиляция физических вычислений (~10-100x быстрее)
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
        self.active = np.zeros(self.max_particles, dtype=np.bool_)

        # Эмиссия частиц
        self.emit_interval = 0.005
        self.emit_timer = 0.0
        self.particles_emitted = 0
        self.next_particle_idx = 0

        # Буферы для рендеринга (переиспользуем, не создаём каждый кадр)
        self._colors_buffer = np.zeros((self.max_particles, 4), dtype=np.float32)
        self._visible_indices = np.zeros(self.max_particles, dtype=np.int32)

    def _emit_particles_batch(self, count: int):
        """Эмиссия пачки частиц с использованием JIT"""
        if count <= 0:
            return

        # Генерируем случайные значения заранее (Numba не поддерживает все numpy.random)
        random_angles = np.random.uniform(0, 2 * np.pi, count).astype(np.float32)
        random_speeds = np.random.uniform(0.7, 1.3, count).astype(np.float32)
        random_sizes = np.random.uniform(5, 20, count).astype(np.float32)
        random_lifetimes = np.random.uniform(0.5, 1.2, count).astype(np.float32)

        self.next_particle_idx = emit_particles_batch(
            self.positions,
            self.velocities,
            self.sizes,
            self.lifetimes,
            self.max_lifetimes,
            self.active,
            float(self.center[0]),
            float(self.center[1]),
            self.initial_speed,
            self.next_particle_idx,
            count,
            self.max_particles,
            random_angles,
            random_speeds,
            random_sizes,
            random_lifetimes
        )

    def _update(self, dt: float):
        """Обновление частиц с использованием Numba JIT"""
        # Эмиссия новых частиц
        if self.progress < 0.7 and self.particles_emitted < self.particle_count:
            self.emit_timer += dt
            particles_to_emit = 0
            while self.emit_timer >= self.emit_interval and self.particles_emitted < self.particle_count:
                self.emit_timer -= self.emit_interval
                self.particles_emitted += 1
                particles_to_emit += 1

            if particles_to_emit > 0:
                self._emit_particles_batch(particles_to_emit)

        # Проверяем есть ли активные частицы
        if not np.any(self.active):
            if self.elapsed >= self.duration:
                self.finished = True
            return

        # JIT-компилированное обновление физики (очень быстро!)
        update_particles_physics(
            self.positions,
            self.velocities,
            self.sizes,
            self.lifetimes,
            self.max_lifetimes,
            self.active,
            self.gravity,
            dt
        )

        # Проверяем завершение
        if self.elapsed >= self.duration and not np.any(self.active):
            self.finished = True

    def render(self, renderer: Renderer):
        """Отрисовка частиц - оптимизированная версия с Numba"""
        if self.finished:
            return

        if not np.any(self.active):
            return

        # JIT-компилированное вычисление цветов
        visible_count = compute_particle_colors(
            self.lifetimes,
            self.max_lifetimes,
            self.sizes,
            self.active,
            self.base_color,
            self._colors_buffer,
            self._visible_indices
        )

        if visible_count == 0:
            return

        # Получаем данные видимых частиц
        visible_idx = self._visible_indices[:visible_count]
        positions = self.positions[visible_idx]
        sizes = self.sizes[visible_idx]
        colors = self._colors_buffer[:visible_count]

        # Instanced rendering
        if hasattr(renderer, 'render_circles_instanced'):
            renderer.render_circles_instanced(
                positions,
                sizes,
                colors,
                ring_width=0.5
            )
        else:
            # Fallback: обычный рендеринг
            for i in range(visible_count):
                renderer.render_circle(
                    center=(float(positions[i, 0]), float(positions[i, 1])),
                    radius=float(sizes[i]),
                    alpha=float(colors[i, 3]),
                    color=(float(colors[i, 0]), float(colors[i, 1]),
                           float(colors[i, 2]), float(colors[i, 3])),
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



