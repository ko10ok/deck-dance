"""
Базовый класс сцены
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Tuple, List, Optional


@dataclass
class Scene:
    """
    Сцена - контейнер для настроек отображения и анимаций.

    Сцены можно расширять, добавляя новые параметры и конфигурации анимаций.
    """

    # Основные параметры
    name: str = "Untitled Scene"
    background_color: Tuple[float, float, float, float] = (0.1, 0.1, 0.15, 1.0)

    # Конфигурации анимаций
    # Ключ - тип анимации, значение - словарь параметров
    animation_configs: Dict[str, Dict[str, Any]] = field(default_factory=dict)

    # Дополнительные параметры сцены
    metadata: Dict[str, Any] = field(default_factory=dict)

    # Доступные анимации для этой сцены (список имён)
    available_animations: List[str] = field(default_factory=list)

    # Индекс текущей выбранной анимации
    current_animation_index: int = 0

    @property
    def current_animation_name(self) -> Optional[str]:
        """Имя текущей выбранной анимации"""
        if self.available_animations and 0 <= self.current_animation_index < len(self.available_animations):
            return self.available_animations[self.current_animation_index]
        return None

    def next_animation(self):
        """Переключение на следующую анимацию"""
        if self.available_animations:
            self.current_animation_index = (self.current_animation_index + 1) % len(self.available_animations)

    def prev_animation(self):
        """Переключение на предыдущую анимацию"""
        if self.available_animations:
            self.current_animation_index = (self.current_animation_index - 1) % len(self.available_animations)

    def get_animation_config(self, animation_type: str) -> Dict[str, Any]:
        """Получение конфигурации для типа анимации"""
        return self.animation_configs.get(animation_type, {})

    def get_current_animation_config(self) -> Dict[str, Any]:
        """Получение конфигурации для текущей выбранной анимации"""
        name = self.current_animation_name
        if name:
            return self.get_animation_config(name)
        return {}

    def set_animation_config(self, animation_type: str, config: Dict[str, Any]):
        """Установка конфигурации для типа анимации"""
        self.animation_configs[animation_type] = config

    def to_dict(self) -> Dict[str, Any]:
        """Сериализация сцены в словарь"""
        return {
            "name": self.name,
            "background_color": list(self.background_color),
            "animation_configs": self.animation_configs,
            "metadata": self.metadata,
            "current_animation_index": self.current_animation_index
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any], available_animations: List[str] = None) -> 'Scene':
        """Создание сцены из словаря"""
        return cls(
            name=data.get("name", "Untitled Scene"),
            background_color=tuple(data.get("background_color", [0.1, 0.1, 0.15, 1.0])),
            animation_configs=data.get("animation_configs", {}),
            metadata=data.get("metadata", {}),
            available_animations=available_animations or [],
            current_animation_index=data.get("current_animation_index", 0)
        )

