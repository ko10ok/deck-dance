"""
Меню выбора сцен (появляется при зажатии X)
"""

import pygame
import numpy as np
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.app import App
    from src.core.input_manager import InputManager
    from src.core.renderer import Renderer


class ScenePicker:
    """Меню быстрого выбора сцен"""

    def __init__(self, app: 'App'):
        self.app = app
        self.selected_index = 0

        pygame.font.init()
        self.font = pygame.font.Font(None, 32)
        self.font_small = pygame.font.Font(None, 24)

    def handle_input(self, input_manager: 'InputManager'):
        """Обработка ввода в меню"""
        scene_count = len(self.app.scene_manager.scenes)
        if scene_count == 0:
            return

        # Навигация D-Pad
        if input_manager.is_dpad_pressed("up"):
            self.selected_index = (self.selected_index - 1) % scene_count
        if input_manager.is_dpad_pressed("down"):
            self.selected_index = (self.selected_index + 1) % scene_count

        # Навигация клавиатурой
        if input_manager.is_key_pressed(pygame.K_UP):
            self.selected_index = (self.selected_index - 1) % scene_count
        if input_manager.is_key_pressed(pygame.K_DOWN):
            self.selected_index = (self.selected_index + 1) % scene_count

        # Выбор сцены при отпускании X или нажатии A
        # (выбор происходит когда отпускают X, см. playback_screen)

        # Обновляем выбор в scene_manager при навигации
        self.app.scene_manager.select_scene(self.selected_index)

    def render(self, renderer: 'Renderer'):
        """Отрисовка меню выбора сцен"""
        width, height = renderer.window_size

        # Полупрозрачный фон
        surface = pygame.Surface((width, height), pygame.SRCALPHA)
        pygame.draw.rect(surface, (0, 0, 0, 180), (0, 0, width, height))

        # Заголовок
        title = self.font.render("Выбор сцены (отпустите X)", True, (255, 255, 255))
        title_rect = title.get_rect(center=(width // 2, 80))
        surface.blit(title, title_rect)

        # Список сцен
        scenes = self.app.scene_manager.get_scene_names()
        start_y = 150

        for i, name in enumerate(scenes):
            is_selected = (i == self.selected_index)
            is_current = (i == self.app.scene_manager.current_index)

            # Цвет текста
            if is_selected:
                color = (100, 200, 255)
            elif is_current:
                color = (200, 200, 100)
            else:
                color = (180, 180, 180)

            # Индикаторы
            prefix = ""
            if is_selected:
                prefix += "► "
            if is_current:
                prefix += "● "

            text = self.font.render(f"{prefix}{name}", True, color)
            rect = text.get_rect(center=(width // 2, start_y + i * 40))
            surface.blit(text, rect)

        # Подсказка
        hint = self.font_small.render(
            "↑↓ Выбор  |  Отпустите X для подтверждения",
            True, (128, 128, 128)
        )
        hint_rect = hint.get_rect(center=(width // 2, height - 50))
        surface.blit(hint, hint_rect)

        # Рендеринг
        self._render_pygame_surface(surface, renderer)

    def _render_pygame_surface(self, surface: pygame.Surface, renderer: 'Renderer'):
        """Рендеринг pygame surface через OpenGL"""
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

