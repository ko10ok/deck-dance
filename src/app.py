"""
Главный класс приложения
"""

import pygame
import moderngl
from src.config import (
    WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE,
    TARGET_FPS, FULLSCREEN_DEFAULT
)
from src.core.input_manager import InputManager
from src.core.renderer import Renderer
from src.core.scene_manager import SceneManager
from src.screens.main_menu import MainMenuScreen
from src.screens.playback_screen import PlaybackScreen
from src.screens.editor_screen import EditorScreen


class App:
    """Главный класс приложения"""

    def __init__(self):
        # Инициализация pygame
        pygame.init()
        pygame.joystick.init()

        # Настройки окна
        self.fullscreen = FULLSCREEN_DEFAULT
        self.window_size = (WINDOW_WIDTH, WINDOW_HEIGHT)

        # Создаём окно с OpenGL контекстом
        self._create_window()

        # Инициализация подсистем
        self.clock = pygame.time.Clock()
        self.running = True

        # Менеджеры
        self.input_manager = InputManager()
        self.renderer = Renderer(self.ctx, self.window_size)
        self.scene_manager = SceneManager()

        # Экраны
        self.screens = {
            "main_menu": MainMenuScreen(self),
            "playback": PlaybackScreen(self),
            "editor": EditorScreen(self),
        }
        self.current_screen = self.screens["main_menu"]

    def _create_window(self):
        """Создание окна с OpenGL контекстом"""
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MAJOR_VERSION, 3)
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MINOR_VERSION, 3)
        pygame.display.gl_set_attribute(
            pygame.GL_CONTEXT_PROFILE_MASK,
            pygame.GL_CONTEXT_PROFILE_CORE
        )

        flags = pygame.OPENGL | pygame.DOUBLEBUF
        if self.fullscreen:
            flags |= pygame.FULLSCREEN
            # Получаем размер экрана для fullscreen
            info = pygame.display.Info()
            self.window_size = (info.current_w, info.current_h)

        self.screen = pygame.display.set_mode(self.window_size, flags)
        pygame.display.set_caption(WINDOW_TITLE)

        # Создаём ModernGL контекст
        self.ctx = moderngl.create_context()
        self.ctx.enable(moderngl.BLEND)
        self.ctx.blend_func = moderngl.SRC_ALPHA, moderngl.ONE_MINUS_SRC_ALPHA

    def toggle_fullscreen(self):
        """Переключение полноэкранного режима"""
        self.fullscreen = not self.fullscreen
        self._create_window()
        self.renderer.resize(self.window_size)

    def switch_screen(self, screen_name: str):
        """Переключение на другой экран"""
        if screen_name in self.screens:
            self.current_screen.on_exit()
            self.current_screen = self.screens[screen_name]
            self.current_screen.on_enter()

    def run(self):
        """Главный игровой цикл"""
        self.current_screen.on_enter()

        while self.running:
            dt = self.clock.tick(TARGET_FPS) / 1000.0  # Delta time в секундах

            # Обработка событий
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False

            # Обновление ввода
            self.input_manager.update(events, dt)

            # Обновление текущего экрана
            self.current_screen.update(dt)
            self.current_screen.handle_input(self.input_manager)

            # Рендеринг
            self.ctx.clear(0.1, 0.1, 0.15, 1.0)
            self.current_screen.render(self.renderer)

            pygame.display.flip()

        self.cleanup()

    def quit(self):
        """Выход из приложения"""
        self.running = False

    def cleanup(self):
        """Очистка ресурсов"""
        self.renderer.cleanup()
        pygame.quit()

