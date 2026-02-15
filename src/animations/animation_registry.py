"""
Реестр анимаций - централизованное хранение всех типов анимаций
"""

from typing import Dict, Type, List, Any, Tuple, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from src.animations.base_animation import BaseAnimation


class AnimationRegistry:
    """Глобальный реестр всех доступных типов анимаций"""

    _animations: Dict[str, Type['BaseAnimation']] = {}
    _default_configs: Dict[str, Dict[str, Any]] = {}

    @classmethod
    def register(cls, name: str, animation_class: Type['BaseAnimation'],
                 default_config: Dict[str, Any] = None):
        """Регистрация типа анимации"""
        cls._animations[name] = animation_class
        cls._default_configs[name] = default_config or {}

    @classmethod
    def get(cls, name: str) -> Type['BaseAnimation']:
        """Получение класса анимации по имени"""
        return cls._animations.get(name)

    @classmethod
    def get_default_config(cls, name: str) -> Dict[str, Any]:
        """Получение дефолтной конфигурации для типа анимации"""
        return cls._default_configs.get(name, {}).copy()

    @classmethod
    def get_all_names(cls) -> List[str]:
        """Получение списка всех зарегистрированных имён анимаций"""
        return list(cls._animations.keys())

    @classmethod
    def get_all_default_configs(cls) -> Dict[str, Dict[str, Any]]:
        """Получение всех дефолтных конфигураций"""
        return {name: config.copy() for name, config in cls._default_configs.items()}

    @classmethod
    def create(cls, name: str, center: Tuple[float, float],
               config: Dict[str, Any] = None) -> Optional['BaseAnimation']:
        """Создание экземпляра анимации по имени с конфигурацией"""
        animation_class = cls.get(name)
        if not animation_class:
            return None

        # Объединяем дефолтную конфигурацию с переданной
        final_config = cls.get_default_config(name)
        if config:
            final_config.update(config)

        return animation_class(center=center, **final_config)


def register_all_animations():
    """Регистрация всех стандартных анимаций"""
    from src.animations.expanding_circle import ExpandingCircleAnimation
    from src.animations.fire_animation import FireAnimation

    AnimationRegistry.register(
        "expanding_circle",
        ExpandingCircleAnimation,
        {
            "color": (1.0, 1.0, 1.0, 1.0),
            "duration": 1.0,
            "max_radius": 150.0,
            "ring_width": 0.15
        }
    )

    AnimationRegistry.register(
        "fire",
        FireAnimation,
        {
            "color": (1.0, 0.4, 0.1, 1.0),
            "duration": 0.7,
            "particle_count": 50,
            "spread": 150.0,
            "initial_speed": 200.0,
            "gravity": (0.0, -400.0)
        }
    )



