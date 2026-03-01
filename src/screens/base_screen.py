"""
Базовый класс экрана
"""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.app import App
    from src.core.input_manager import InputManager
    from src.core.renderer import Renderer


class BaseScreen(ABC):
    """Абстрактный базовый класс для всех экранов приложения"""

    def __init__(self, app: 'App'):
        self.app = app

    def on_enter(self):
        """Вызывается при переходе на этот экран"""
        pass

    def on_exit(self):
        """Вызывается при уходе с этого экрана"""
        pass

    @abstractmethod
    def update(self, dt: float):
        """Обновление логики экрана"""
        pass

    @abstractmethod
    def handle_input(self, input_manager: 'InputManager'):
        """Обработка ввода"""
        pass

    @abstractmethod
    def render(self, renderer: 'Renderer'):
        """Отрисовка экрана"""
        pass

