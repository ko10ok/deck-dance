"""
Пул анимаций для управления множественными независимыми анимациями
"""

from typing import List, TYPE_CHECKING
from src.animations.base_animation import BaseAnimation
from src.config import MAX_CONCURRENT_ANIMATIONS

if TYPE_CHECKING:
    from src.core.renderer import Renderer


class AnimationPool:
    """
    Пул для управления множеством независимых анимаций.
    Поддерживает мультитач и большое количество одновременных анимаций.
    """

    def __init__(self, max_animations: int = MAX_CONCURRENT_ANIMATIONS):
        self.animations: List[BaseAnimation] = []
        self.max_animations = max_animations

    def add(self, animation: BaseAnimation):
        """Добавление новой анимации в пул"""
        # Если превышен лимит, удаляем самые старые
        while len(self.animations) >= self.max_animations:
            self.animations.pop(0)

        self.animations.append(animation)

    def update(self, dt: float):
        """Обновление всех анимаций"""
        # Обновляем все анимации
        for animation in self.animations:
            animation.update(dt)

        # Удаляем завершённые анимации
        self.animations = [a for a in self.animations if not a.finished]

    def render(self, renderer: 'Renderer'):
        """Отрисовка всех анимаций"""
        for animation in self.animations:
            animation.render(renderer)

    def clear(self):
        """Очистка всех анимаций"""
        self.animations.clear()

    def __len__(self) -> int:
        """Количество активных анимаций"""
        return len(self.animations)

