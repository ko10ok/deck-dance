"""
Экран редактора сцен
"""

import pygame
from src.screens.base_screen import BaseScreen
from src.core.input_manager import InputManager
from src.core.renderer import Renderer
from src.config import ControllerButtons


class EditorScreen(BaseScreen):
    """Экран редактирования сцен"""

    def __init__(self, app):
        super().__init__(app)

        self.menu_items = [
            "Новая сцена",
            "Редактировать текущую",
            "Удалить сцену",
            "Перезагрузить сцены",
        ]
        self.selected_index = 0

        pygame.font.init()
        self.font_large = pygame.font.Font(None, 56)
        self.font_medium = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 28)

    def on_enter(self):
        """Сброс при входе"""
        self.selected_index = 0

    def update(self, dt: float):
        """Обновление"""
        pass

    def handle_input(self, input_manager: InputManager):
        """Обработка ввода"""
        # Выход в главное меню
        if input_manager.is_escape_pressed():
            self.app.switch_screen("main_menu")
            return

        # Навигация
        if (input_manager.is_dpad_pressed("up") or
            input_manager.is_key_pressed(pygame.K_w)):
            self.selected_index = (self.selected_index - 1) % len(self.menu_items)

        if (input_manager.is_dpad_pressed("down") or
            input_manager.is_key_pressed(pygame.K_s)):
            self.selected_index = (self.selected_index + 1) % len(self.menu_items)

        # Выбор
        if (input_manager.is_button_pressed(ControllerButtons.A) or
            input_manager.is_key_pressed(pygame.K_RETURN)):
            self._handle_selection()

    def _handle_selection(self):
        """Обработка выбора пункта меню"""
        action = self.menu_items[self.selected_index]

        if action == "Новая сцена":
            self._create_new_scene()
        elif action == "Редактировать текущую":
            self._edit_current_scene()
        elif action == "Удалить сцену":
            self._delete_current_scene()
        elif action == "Перезагрузить сцены":
            self.app.scene_manager.reload_scenes()

    def _create_new_scene(self):
        """Создание новой сцены (заглушка)"""
        from src.scenes.base_scene import Scene
        import random

        # Генерируем случайный цвет
        color = (
            random.uniform(0.05, 0.2),
            random.uniform(0.05, 0.2),
            random.uniform(0.1, 0.3),
            1.0
        )

        scene = Scene(
            name=f"Сцена {len(self.app.scene_manager.scenes) + 1}",
            background_color=color,
            animation_configs={
                "expanding_circle": {
                    "color": (random.random(), random.random(), random.random(), 1.0),
                    "duration": random.uniform(0.5, 2.0),
                    "max_radius": random.uniform(100, 200),
                    "ring_width": random.uniform(0.1, 0.2)
                }
            }
        )

        self.app.scene_manager.add_scene(scene)

    def _edit_current_scene(self):
        """Редактирование текущей сцены (заглушка)"""
        # TODO: Реализовать полноценный редактор
        pass

    def _delete_current_scene(self):
        """Удаление текущей сцены"""
        self.app.scene_manager.remove_scene(
            self.app.scene_manager.current_index
        )

    def render(self, renderer: Renderer):
        """Отрисовка редактора"""
        renderer.ctx.clear(0.08, 0.08, 0.12, 1.0)

        width, height = renderer.window_size
        surface = pygame.Surface((width, height), pygame.SRCALPHA)

        # Заголовок
        title = self.font_large.render("Редактор сцен", True, (255, 255, 255))
        title_rect = title.get_rect(center=(width // 2, 60))
        surface.blit(title, title_rect)

        # Информация о текущей сцене
        scene = self.app.scene_manager.current_scene
        if scene:
            info = self.font_small.render(
                f"Текущая сцена: {scene.name} ({self.app.scene_manager.current_index + 1}/"
                f"{len(self.app.scene_manager.scenes)})",
                True, (180, 180, 180)
            )
            info_rect = info.get_rect(center=(width // 2, 110))
            surface.blit(info, info_rect)

        # Меню редактора
        menu_start_y = 180
        for i, item in enumerate(self.menu_items):
            color = (100, 200, 255) if i == self.selected_index else (180, 180, 180)
            text = self.font_medium.render(item, True, color)
            rect = text.get_rect(center=(width // 2, menu_start_y + i * 50))

            if i == self.selected_index:
                indicator = self.font_medium.render("> ", True, (100, 200, 255))
                ind_rect = indicator.get_rect(right=rect.left - 10, centery=rect.centery)
                surface.blit(indicator, ind_rect)

            surface.blit(text, rect)

        # Список сцен
        scenes_title = self.font_small.render("Доступные сцены:", True, (150, 150, 150))
        surface.blit(scenes_title, (50, height - 200))

        for i, name in enumerate(self.app.scene_manager.get_scene_names()):
            prefix = "► " if i == self.app.scene_manager.current_index else "  "
            scene_text = self.font_small.render(f"{prefix}{name}", True, (120, 120, 120))
            surface.blit(scene_text, (60, height - 170 + i * 25))

        # Подсказки
        hints = "↑↓ Выбор  |  A/Enter Применить  |  Start/ESC Назад"
        hint_surface = self.font_small.render(hints, True, (100, 100, 100))
        hint_rect = hint_surface.get_rect(center=(width // 2, height - 30))
        surface.blit(hint_surface, hint_rect)

        self._render_pygame_surface(surface, renderer)

    def _render_pygame_surface(self, surface: pygame.Surface, renderer: Renderer):
        """Рендеринг pygame surface через OpenGL"""
        import numpy as np

        texture_data = pygame.image.tostring(surface, "RGBA", True)
        texture = renderer.ctx.texture(surface.get_size(), 4, texture_data)
        texture.use()

        vertices = np.array([
            -1.0, -1.0, 0.0, 0.0,
             1.0, -1.0, 1.0, 0.0,
             1.0,  1.0, 1.0, 1.0,
            -1.0,  1.0, 0.0, 1.0,
        ], dtype='f4')

        indices = np.array([0, 1, 2, 0, 2, 3], dtype='i4')

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

        vao.release()
        vbo.release()
        ibo.release()
        texture.release()
        prog.release()

