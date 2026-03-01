"""
Базовый класс анимации
"""

from abc import ABC, abstractmethod
from typing import Tuple, Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from src.core.renderer import Renderer


class BaseAnimation(ABC):
    """Абстрактный базовый класс для всех анимаций"""

    def __init__(
        self,
        center: Tuple[float, float],
        duration: float = 1.0,
        **kwargs
    ):
        self.center = center
        self.duration = duration
        self.elapsed = 0.0
        self.finished = False
        self.kwargs = kwargs

    @property
    def progress(self) -> float:
        """Прогресс анимации от 0 до 1"""
        if self.duration <= 0:
            return 1.0
        return min(self.elapsed / self.duration, 1.0)

    def update(self, dt: float):
        """Обновление состояния анимации"""
        self.elapsed += dt
        if self.elapsed >= self.duration:
            self.finished = True
        self._update(dt)

    @abstractmethod
    def _update(self, dt: float):
        """Внутреннее обновление (для переопределения в наследниках)"""
        pass

    @abstractmethod
    def render(self, renderer: 'Renderer'):
        """Отрисовка анимации"""
        pass

    @classmethod
    def get_config_schema(cls) -> Dict[str, Any]:
        """Схема конфигурации анимации для редактора"""
        return {
            "duration": {"type": "float", "default": 1.0, "min": 0.1, "max": 10.0},
        }

