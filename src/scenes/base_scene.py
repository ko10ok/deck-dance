"""
Базовый класс сцены
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Tuple


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

    def get_animation_config(self, animation_type: str) -> Dict[str, Any]:
        """Получение конфигурации для типа анимации"""
        return self.animation_configs.get(animation_type, {})

    def set_animation_config(self, animation_type: str, config: Dict[str, Any]):
        """Установка конфигурации для типа анимации"""
        self.animation_configs[animation_type] = config

    def to_dict(self) -> Dict[str, Any]:
        """Сериализация сцены в словарь"""
        return {
            "name": self.name,
            "background_color": list(self.background_color),
            "animation_configs": self.animation_configs,
            "metadata": self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Scene':
        """Создание сцены из словаря"""
        return cls(
            name=data.get("name", "Untitled Scene"),
            background_color=tuple(data.get("background_color", [0.1, 0.1, 0.15, 1.0])),
            animation_configs=data.get("animation_configs", {}),
            metadata=data.get("metadata", {})
        )

