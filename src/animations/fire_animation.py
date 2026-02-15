"""
Анимация огня - частицы поднимающегося пламени
"""

import random
import math
from typing import Tuple, Dict, Any, List
from src.animations.base_animation import BaseAnimation
from src.core.renderer import Renderer


class FireParticle:
    """Отдельная частица огня"""

    def __init__(self, x: float, y: float, max_lifetime: float,
                 initial_velocity: Tuple[float, float],
                 gravity: Tuple[float, float] = (0.0, -100.0)):
        self.x = x
        self.y = y
        self.lifetime = 0.0
        self.max_lifetime = max_lifetime

        # Начальная скорость (расходится от центра)
        self.vx = initial_velocity[0]
        self.vy = initial_velocity[1]

        # Вектор тяготения (куда стремятся частицы)
        self.gravity = gravity

        # Размер частицы
        self.size = random.uniform(5, 20)

    @property
    def progress(self) -> float:
        return min(self.lifetime / self.max_lifetime, 1.0)

    @property
    def is_dead(self) -> bool:
        return self.lifetime >= self.max_lifetime

    def update(self, dt: float):
        self.lifetime += dt

        # Применяем тяготение к скорости
        self.vx += self.gravity[0] * dt
        self.vy += self.gravity[1] * dt

        # Обновляем позицию
        self.x += self.vx * dt
        self.y += self.vy * dt

        # Уменьшаем размер со временем
        self.size *= (1.0 - dt * 0.5)


class FireAnimation(BaseAnimation):
    """Анимация огня с системой частиц"""

    def __init__(
        self,
        center: Tuple[float, float],
        color: Tuple[float, float, float, float] = (1.0, 0.4, 0.1, 1.0),
        duration: float = 2.0,
        particle_count: int = 30,
        spread: float = 50.0,
        initial_speed: float = 120.0,
        gravity: Tuple[float, float] = (0.0, -100.0),
        **kwargs
    ):
        super().__init__(center, duration, **kwargs)
        self.color = color
        self.particle_count = particle_count
        self.spread = spread
        self.initial_speed = initial_speed
        self.gravity = gravity

        # Частицы
        self.particles: List[FireParticle] = []

        # Эмиссия частиц
        self.emit_interval = 0.02
        self.emit_timer = 0.0
        self.particles_emitted = 0

    def _update(self, dt: float):
        """Обновление частиц огня"""
        # Эмиссия новых частиц в первой половине анимации
        if self.progress < 0.7 and self.particles_emitted < self.particle_count:
            self.emit_timer += dt
            while self.emit_timer >= self.emit_interval and self.particles_emitted < self.particle_count:
                self._emit_particle()
                self.emit_timer -= self.emit_interval
                self.particles_emitted += 1

        # Обновление частиц
        for particle in self.particles:
            particle.update(dt)

        # Удаление мёртвых частиц
        self.particles = [p for p in self.particles if not p.is_dead]

        # Анимация завершается когда все частицы исчезли и время вышло
        if self.elapsed >= self.duration and not self.particles:
            self.finished = True

    def _emit_particle(self):
        """Эмиссия одной частицы"""
        # Частица появляется в центре
        x = self.center[0]
        y = self.center[1]

        # Случайный угол для направления разлёта от центра (по кругу)
        angle = random.uniform(0, 2 * math.pi)

        # Случайная начальная скорость с небольшим разбросом
        speed = self.initial_speed * random.uniform(0.7, 1.3)

        # Начальная скорость - расходятся от центра
        vx = math.cos(angle) * speed
        vy = math.sin(angle) * speed

        particle = FireParticle(
            x, y,
            max_lifetime=random.uniform(0.5, 1.2),
            initial_velocity=(vx, vy),
            gravity=self.gravity
        )
        self.particles.append(particle)

    def render(self, renderer: Renderer):
        """Отрисовка частиц огня"""
        if self.finished:
            return

        for particle in self.particles:
            # Цвет меняется от жёлтого к красному по мере угасания
            progress = particle.progress

            # Интерполяция цвета: жёлтый -> оранжевый -> красный
            r = self.color[0]
            g = self.color[1] * (1.0 - progress * 0.7)
            b = self.color[2] * (1.0 - progress)

            # Прозрачность уменьшается к концу жизни частицы
            alpha = (1.0 - progress) * self.color[3]

            if alpha > 0.01 and particle.size > 1:
                renderer.render_circle(
                    center=(particle.x, particle.y),
                    radius=particle.size,
                    alpha=alpha,
                    color=(r, g, b, 1.0),
                    ring_width=0.5  # Заполненный круг
                )

    @classmethod
    def get_config_schema(cls) -> Dict[str, Any]:
        """Схема конфигурации для редактора"""
        schema = super().get_config_schema()
        schema.update({
            "color": {"type": "color", "default": (1.0, 0.4, 0.1, 1.0)},
            "particle_count": {"type": "int", "default": 30, "min": 5, "max": 100},
            "spread": {"type": "float", "default": 50.0, "min": 10.0, "max": 200.0},
            "initial_speed": {"type": "float", "default": 120.0, "min": 20.0, "max": 300.0},
            "gravity": {"type": "vector2", "default": (0.0, -100.0)},
        })
        return schema


