"""
Экран воспроизведения - основной режим с анимациями
"""

import pygame
from typing import List, Tuple
from src.screens.base_screen import BaseScreen
from src.core.input_manager import InputManager
from src.core.renderer import Renderer
from src.config import ControllerButtons
from src.animations.animation_pool import AnimationPool
from src.animations.expanding_circle import ExpandingCircleAnimation
from src.ui.scene_picker import ScenePicker


class PlaybackScreen(BaseScreen):
    """Экран воспроизведения с 3D пространством и анимациями"""

    def __init__(self, app):
        super().__init__(app)

        # Пул анимаций
        self.animation_pool = AnimationPool()

        # UI элементы
        self.scene_picker = ScenePicker(app)
        self.show_scene_picker = False

        # Состояние
        self.pending_touches: List[Tuple[int, int]] = []

    def on_enter(self):
        """Инициализация при входе на экран"""
        self.animation_pool.clear()
        self.show_scene_picker = False

    def on_exit(self):
        """Очистка при выходе"""
        self.animation_pool.clear()

    def update(self, dt: float):
        """Обновление анимаций и логики"""
        # Обновление всех анимаций
        self.animation_pool.update(dt)

        # Создание анимаций из отложенных касаний
        for pos in self.pending_touches:
            self._create_animation_at(pos)
        self.pending_touches.clear()

    def handle_input(self, input_manager: InputManager):
        """Обработка ввода"""
        # Проверяем зажатие X для показа меню сцен
        if input_manager.is_modifier_active(ControllerButtons.X):
            self.show_scene_picker = True
            self.scene_picker.handle_input(input_manager)
        else:
            if self.show_scene_picker:
                self.show_scene_picker = False

            self._handle_normal_input(input_manager)

    def _handle_normal_input(self, input_manager: InputManager):
        """Обработка обычного ввода (без модификаторов)"""
        # Выход в меню
        if input_manager.is_escape_pressed():
            self.app.switch_screen("main_menu")
            return

        # Переключение полноэкранного режима
        if input_manager.is_option_pressed():
            self.app.toggle_fullscreen()

        # Смена сцен влево/вправо
        if (input_manager.is_dpad_pressed("left") or
            input_manager.is_key_pressed(pygame.K_LEFT)):
            self.app.scene_manager.prev_scene()

        if (input_manager.is_dpad_pressed("right") or
            input_manager.is_key_pressed(pygame.K_RIGHT)):
            self.app.scene_manager.next_scene()

        # Создание анимации по клику мыши
        if input_manager.is_mouse_pressed(1):  # ЛКМ
            pos = input_manager.get_mouse_pos()
            self.pending_touches.append(pos)

        # Создание анимации по нажатию A
        if input_manager.is_button_pressed(ControllerButtons.A):
            # Создаём анимацию в центре экрана
            center = (
                self.app.window_size[0] // 2,
                self.app.window_size[1] // 2
            )
            self.pending_touches.append(center)

        # Обработка мультитача
        for touch_id, pos in input_manager.get_touch_points().items():
            # Создаём анимацию только для новых касаний
            # (здесь упрощённо - при каждом кадре с касанием)
            pass  # Мультитач обрабатывается через события FINGERDOWN

    def _create_animation_at(self, pos: Tuple[int, int]):
        """Создание анимации в указанной точке"""
        scene = self.app.scene_manager.current_scene
        if not scene:
            return

        # Получаем конфигурацию анимации из сцены
        config = scene.animation_configs.get("expanding_circle", {})

        animation = ExpandingCircleAnimation(
            center=pos,
            color=config.get("color", (1.0, 1.0, 1.0, 1.0)),
            duration=config.get("duration", 1.0),
            max_radius=config.get("max_radius", 150.0),
            ring_width=config.get("ring_width", 0.15)
        )

        self.animation_pool.add(animation)

    def render(self, renderer: Renderer):
        """Отрисовка экрана"""
        # Чёрный фон
        renderer.ctx.clear(0.0, 0.0, 0.0, 1.0)

        # Отрисовка всех анимаций
        self.animation_pool.render(renderer)

        # Отрисовка UI
        self._render_ui(renderer)

        # Отрисовка меню выбора сцен
        if self.show_scene_picker:
            self.scene_picker.render(renderer)

    def _render_ui(self, renderer: Renderer):
        """Отрисовка UI элементов"""
        scene = self.app.scene_manager.current_scene
        if not scene:
            return

        # Отображение названия текущей сцены
        width, height = renderer.window_size

        surface = pygame.Surface((width, height), pygame.SRCALPHA)
        font = pygame.font.Font(None, 32)

        # Название сцены
        scene_text = font.render(f"Сцена: {scene.name}", True, (255, 255, 255, 180))
        surface.blit(scene_text, (20, 20))

        # Количество активных анимаций
        anim_count = len(self.animation_pool.animations)
        count_text = font.render(f"Анимаций: {anim_count}", True, (255, 255, 255, 180))
        surface.blit(count_text, (20, 50))

        # Подсказки
        hints = [
            "←→ Смена сцены",
            "Зажать X: меню сцен",
            "Клик/A: анимация",
            "Select: полный экран",
            "Start: выход"
        ]
        hint_font = pygame.font.Font(None, 24)
        for i, hint in enumerate(hints):
            hint_surf = hint_font.render(hint, True, (150, 150, 150))
            surface.blit(hint_surf, (width - 200, 20 + i * 25))

        # Рендеринг surface
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
                vec4 color = texture(tex, v_texcoord);
                if (color.a < 0.01) discard;
                fragColor = color;
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

