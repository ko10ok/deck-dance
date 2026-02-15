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
               config: Dict[str, Any] = None, **kwargs) -> Optional['BaseAnimation']:
        """
        Создание экземпляра анимации по имени с конфигурацией.

        Args:
            name: Имя зарегистрированной анимации
            center: Центр анимации (x, y)
            config: Базовая конфигурация (из сцены)
            **kwargs: Дополнительные параметры для переопределения конфига
        """
        animation_class = cls.get(name)
        if not animation_class:
            return None

        # Объединяем: default -> config -> kwargs (kwargs имеет наивысший приоритет)
        final_config = cls.get_default_config(name)
        if config:
            final_config.update(config)
        if kwargs:
            final_config.update(kwargs)

        return animation_class(center=center, **final_config)


def register_all_animations():
    """Регистрация всех стандартных анимаций"""
    from src.animations.expanding_circle import ExpandingCircleAnimation
    from src.animations.fire_animation_optimized import FireAnimationOptimized
    from src.animations.bouncing_line import BouncingLineAnimation

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

    # AnimationRegistry.register(
    #     "fire",
    #     FireAnimation,
    #     {
    #         "color": (1.0, 0.4, 0.1, 1.0),
    #         "duration": 0.7,
    #         "particle_count": 50,
    #         "spread": 150.0,
    #         "initial_speed": 200.0,
    #         "gravity": (0.0, -400.0)
    #     }
    # )

    # Версия огня (для большого количества частиц)
    AnimationRegistry.register(
        "fire",
        FireAnimationOptimized,
        {
            "color": (1.0, 0.4, 0.1, 1.0),
            "duration": 0.7,
            "particle_count": 50,
            "spread": 150.0,
            "initial_speed": 250.0,
            "gravity": (0.0, -400.0)
        }
    )

    # Оптимизированная версия огня (для большого количества частиц)
    AnimationRegistry.register(
        "spark",
        FireAnimationOptimized,
        {
            "color": (0.3, 0.5, 1.0, 1.0),
            "duration": 0.7,
            "particle_count": 10,
            "spread": 300.0,
            "initial_speed": 500.0,
            "gravity": (0.0, 0.0)
        }
    )

    # Отскакивающая линия в расширяющемся квадрате
    AnimationRegistry.register(
        "bouncing_line",
        BouncingLineAnimation,
        {
            "color": (0.0, 1.0, 1.0, 1.0),
            "duration": 1.0,
            "initial_box_size": 100.0,
            "max_box_size": 1500.0,
            "speed": 600.0,
            "expand": True,
            "line_style": "solid"
        }
    )

    # Отскакивающая линия в сужающемся квадрате
    AnimationRegistry.register(
        "bouncing_line_shrink",
        BouncingLineAnimation,
        {
            "color": (1.0, 0.5, 0.0, 1.0),
            "duration": 1.0,
            "initial_box_size": 100.0,
            "max_box_size": 1500.0,
            "speed": 300.0,
            "expand": False,
            "line_style": "dotted"
        }
    )

