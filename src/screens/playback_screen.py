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
from src.animations.animation_registry import AnimationRegistry
from src.ui.scene_picker import ScenePicker
from src.utils.color_picker import ColorPicker


class PlaybackScreen(BaseScreen):
    """Экран воспроизведения с 3D пространством и анимациями"""

    def __init__(self, app):
        super().__init__(app)

        # Пул анимаций
        self.animation_pool = AnimationPool()

        # UI элементы
        self.scene_picker = ScenePicker(app)
        self.show_scene_picker = False
        self.show_verbose_control_ui = False  # По умолчанию скрыто

        # Состояние
        self.pending_touches: List[Tuple[int, int]] = []

        # Выбор цвета через левый джойстик
        self.current_hue = 0.0  # Оттенок 0-360
        self.current_color = (1.0, 0.0, 0.0, 1.0)  # RGBA

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

        # Переключение отображения подсказок (Y)
        if input_manager.is_button_pressed(ControllerButtons.Y):
            self.show_verbose_control_ui = not self.show_verbose_control_ui

        # === Выбор цвета через ColorPicker ===
        color_result = ColorPicker.get_color(
            pressed_keys=list(input_manager.state.keys_just_pressed),
            stick=input_manager.state.left_stick
        )
        if color_result:
            self.current_hue, self.current_color = color_result

        # Смена сцен влево/вправо
        if (input_manager.is_dpad_pressed("left") or
            input_manager.is_key_pressed(pygame.K_a)):
            self.app.scene_manager.prev_scene()

        if (input_manager.is_dpad_pressed("right") or
            input_manager.is_key_pressed(pygame.K_d)):
            self.app.scene_manager.next_scene()

        # Смена анимации вверх/вниз (для текущей сцены)
        scene = self.app.scene_manager.current_scene
        if scene:
            if (input_manager.is_dpad_pressed("up") or
                input_manager.is_key_pressed(pygame.K_w)):
                scene.prev_animation()

            if (input_manager.is_dpad_pressed("down") or
                input_manager.is_key_pressed(pygame.K_s)):
                scene.next_animation()

        # Создание анимации по клику мыши
        if input_manager.is_mouse_pressed(3):  # ЛКМ
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
            # Создаём анимацию для касаний
            self.pending_touches.append(pos)

    def _create_animation_at(self, pos: Tuple[int, int]):
        """Создание анимации в указанной точке"""
        scene = self.app.scene_manager.current_scene
        if not scene:
            return

        # Получаем имя текущей выбранной анимации для этой сцены
        animation_name = scene.current_animation_name
        if not animation_name:
            return

        # Получаем конфигурацию анимации из сцены
        config = scene.get_animation_config(animation_name)

        # Создаём анимацию через реестр с переопределением цвета через kwargs
        animation = AnimationRegistry.create(
            animation_name,
            center=pos,
            config=config,
            color=self.current_color
        )
        if animation:
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
        if not self.show_verbose_control_ui:
            return

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

        # Текущий тип анимации
        anim_name = scene.current_animation_name or "нет"
        anim_type_text = font.render(f"Анимация: {anim_name}", True, (255, 255, 255, 180))
        surface.blit(anim_type_text, (20, 50))

        # Количество активных анимаций
        anim_count = len(self.animation_pool.animations)
        count_text = font.render(f"Активных: {anim_count}", True, (255, 255, 255, 180))
        surface.blit(count_text, (20, 80))

        # Подсказки
        hints = [
            "←→ Смена сцены",
            "↑↓ Смена анимации",
            "Зажать X: меню сцен",
            "Клик/A: анимация",
            "Y: скрыть UI",
            "Select: полный экран",
            "Start: выход"
        ]
        hint_font = pygame.font.Font(None, 24)
        hints_x = width - 200
        y_offset = 20

        for hint in hints:
            hint_surf = hint_font.render(hint, True, (150, 150, 150))
            surface.blit(hint_surf, (hints_x, y_offset))
            y_offset += 25

        # Отображение текущего цвета (текст + квадратик)
        y_offset += 10  # Небольшой отступ
        color_text = hint_font.render(f"Цвет: {int(self.current_hue)}°", True, (150, 150, 150))
        surface.blit(color_text, (hints_x, y_offset))

        # Квадратик с цветом рядом с текстом
        color_rect_x = hints_x + color_text.get_width() + 10
        color_rect_size = 18
        color_rgb = (
            int(self.current_color[0] * 255),
            int(self.current_color[1] * 255),
            int(self.current_color[2] * 255)
        )
        pygame.draw.rect(surface, color_rgb, (color_rect_x, y_offset, color_rect_size, color_rect_size))
        pygame.draw.rect(surface, (100, 100, 100), (color_rect_x, y_offset, color_rect_size, color_rect_size), 1)

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

