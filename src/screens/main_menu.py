"""
Главное меню - выбор режима
"""

import pygame
from src.screens.base_screen import BaseScreen
from src.core.input_manager import InputManager
from src.core.renderer import Renderer
from src.config import ControllerButtons


class MainMenuScreen(BaseScreen):
    """Экран главного меню для выбора режима"""

    def __init__(self, app):
        super().__init__(app)
        self.menu_items = [
            ("Воспроизведение", "playback"),
            ("Редактор сцен", "editor"),
            ("Выход", "quit")
        ]
        self.selected_index = 0

        # Для отрисовки текста
        pygame.font.init()
        self.font_large = pygame.font.Font(None, 72)
        self.font_medium = pygame.font.Font(None, 48)

        # Текстуры для текста
        self.text_surfaces = {}
        self._create_text_surfaces()

    def _create_text_surfaces(self):
        """Создание поверхностей с текстом"""
        # Заголовок
        self.title_surface = self.font_large.render(
            "Toc Vi Paint", True, (255, 255, 255)
        )

        # Пункты меню
        self.menu_surfaces = []
        for item_text, _ in self.menu_items:
            surface = self.font_medium.render(item_text, True, (200, 200, 200))
            surface_selected = self.font_medium.render(item_text, True, (100, 200, 255))
            self.menu_surfaces.append((surface, surface_selected))

    def on_enter(self):
        """Сброс выбора при входе"""
        self.selected_index = 0

    def update(self, dt: float):
        """Обновление меню"""
        pass

    def handle_input(self, input_manager: InputManager):
        """Обработка ввода в меню"""
        # Навигация вверх/вниз
        if (input_manager.is_dpad_pressed("up") or
            input_manager.is_key_pressed(pygame.K_w)):
            self.selected_index = (self.selected_index - 1) % len(self.menu_items)

        if (input_manager.is_dpad_pressed("down") or
            input_manager.is_key_pressed(pygame.K_s)):
            self.selected_index = (self.selected_index + 1) % len(self.menu_items)

        # Выбор пункта
        if (input_manager.is_button_pressed(ControllerButtons.A) or
            input_manager.is_key_pressed(pygame.K_RETURN) or
            input_manager.is_key_pressed(pygame.K_SPACE)):
            self._select_current_item()

        # Выход (возврат в режим воспроизведения)
        if input_manager.is_escape_pressed():
            self.app.switch_screen("playback")

    def _select_current_item(self):
        """Обработка выбора текущего пункта меню"""
        _, action = self.menu_items[self.selected_index]

        if action == "quit":
            self.app.quit()
        elif action in ("playback", "editor"):
            self.app.switch_screen(action)

    def render(self, renderer: Renderer):
        """Отрисовка меню"""
        # Используем pygame для 2D рендеринга поверх OpenGL
        # Рисуем простой фон
        renderer.ctx.clear(0.1, 0.1, 0.15, 1.0)

        # Получаем размеры окна
        width, height = renderer.window_size

        # Создаём временную поверхность pygame
        surface = pygame.Surface((width, height), pygame.SRCALPHA)

        # Рисуем заголовок
        title_rect = self.title_surface.get_rect(center=(width // 2, height // 4))
        surface.blit(self.title_surface, title_rect)

        # Рисуем пункты меню
        menu_start_y = height // 2
        for i, (normal_surf, selected_surf) in enumerate(self.menu_surfaces):
            surf = selected_surf if i == self.selected_index else normal_surf
            rect = surf.get_rect(center=(width // 2, menu_start_y + i * 60))

            # Индикатор выбора
            if i == self.selected_index:
                indicator = self.font_medium.render("> ", True, (100, 200, 255))
                ind_rect = indicator.get_rect(right=rect.left - 10, centery=rect.centery)
                surface.blit(indicator, ind_rect)

            surface.blit(surf, rect)

        # Подсказки управления
        hint_text = "↑↓ Выбор  |  A/Enter Подтвердить  |  ESC Назад"
        hint_surface = pygame.font.Font(None, 28).render(hint_text, True, (128, 128, 128))
        hint_rect = hint_surface.get_rect(center=(width // 2, height - 50))
        surface.blit(hint_surface, hint_rect)

        # Конвертируем pygame surface в OpenGL текстуру и рисуем
        self._render_pygame_surface(surface, renderer)

    def _render_pygame_surface(self, surface: pygame.Surface, renderer: Renderer):
        """Рендеринг pygame surface через OpenGL"""
        # Конвертируем surface в текстуру
        texture_data = pygame.image.tostring(surface, "RGBA", True)

        texture = renderer.ctx.texture(surface.get_size(), 4, texture_data)
        texture.use()

        # Создаём простой квад для отрисовки
        import numpy as np

        vertices = np.array([
            -1.0, -1.0, 0.0, 0.0,
             1.0, -1.0, 1.0, 0.0,
             1.0,  1.0, 1.0, 1.0,
            -1.0,  1.0, 0.0, 1.0,
        ], dtype='f4')

        indices = np.array([0, 1, 2, 0, 2, 3], dtype='i4')

        # Простой шейдер для текстуры
        prog = renderer.ctx.program(
            vertex_shader="""
            #version 330 core
            in vec2 in_position;
            in vec2 in_texcoord;
            out vec2 v_texcoord;
            void main() {
                gl_Position = vec4(in_position, 0.0, 1.0);
                v_texcoord = in_texcoord;
            }
            """,
            fragment_shader="""
            #version 330 core
            in vec2 v_texcoord;
            out vec4 fragColor;
            uniform sampler2D tex;
            void main() {
                fragColor = texture(tex, v_texcoord);
            }
            """
        )

        vbo = renderer.ctx.buffer(vertices.tobytes())
        ibo = renderer.ctx.buffer(indices.tobytes())
        vao = renderer.ctx.vertex_array(prog, [(vbo, '2f 2f', 'in_position', 'in_texcoord')], ibo)

        vao.render()

        # Очистка
        vao.release()
        vbo.release()
        ibo.release()
        texture.release()
        prog.release()

