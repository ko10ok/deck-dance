"""
Менеджер ввода - обработка контроллера и клавиатуры
с поддержкой модификаторов (зажатых кнопок)
"""
from math import trunc

import pygame
from typing import Dict, Set, Tuple, Optional
from dataclasses import dataclass, field
from src.config import (
    ControllerButtons, ControllerAxes,
    MODIFIER_HOLD_TIME
)


@dataclass
class ButtonState:
    """Состояние кнопки"""
    pressed: bool = False       # Нажата в этом кадре
    released: bool = False      # Отпущена в этом кадре
    held: bool = False          # Удерживается
    hold_time: float = 0.0      # Время удержания


@dataclass
class InputState:
    """Полное состояние ввода"""
    # Кнопки контроллера
    buttons: Dict[int, ButtonState] = field(default_factory=dict)

    # D-Pad (HAT)
    dpad: Tuple[int, int] = (0, 0)  # (x, y) -1, 0, 1
    dpad_pressed: Dict[str, bool] = field(default_factory=dict)

    # Аналоговые стики
    left_stick: Tuple[float, float] = (0.0, 0.0)
    right_stick: Tuple[float, float] = (0.0, 0.0)

    # Триггеры
    left_trigger: float = 0.0
    right_trigger: float = 0.0

    # Клавиатура
    keys_pressed: Set[int] = field(default_factory=set)
    keys_just_pressed: Set[int] = field(default_factory=set)
    keys_just_released: Set[int] = field(default_factory=set)

    # Мышь/Тачскрин
    mouse_pos: Tuple[int, int] = (0, 0)
    mouse_buttons: Dict[int, bool] = field(default_factory=dict)
    mouse_just_pressed: Set[int] = field(default_factory=set)
    touch_points: Dict[int, Tuple[int, int]] = field(default_factory=dict)

    # Модификаторы (зажатые кнопки)
    active_modifiers: Set[int] = field(default_factory=set)


class InputManager:
    """Менеджер ввода с поддержкой контроллера и модификаторов"""

    # Кнопки которые могут быть модификаторами
    MODIFIER_BUTTONS = {
        ControllerButtons.X,
        ControllerButtons.Y,
        ControllerButtons.L1,
        ControllerButtons.R1,
    }

    DEADZONE = 0.15  # Мёртвая зона для стиков

    def __init__(self):
        self.state = InputState()
        self.joystick: Optional[pygame.joystick.Joystick] = None
        self._prev_buttons: Dict[int, bool] = {}
        self._prev_dpad: Tuple[int, int] = (0, 0)
        self._prev_keys: Set[int] = set()
        self._prev_mouse: Dict[int, bool] = {}

        self._init_joystick()

    def _init_joystick(self):
        """Инициализация первого найденного джойстика"""
        if pygame.joystick.get_count() > 0:
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()
            print(f"Контроллер найден: {self.joystick.get_name()}")
        else:
            print("Контроллер не найден, используйте клавиатуру/мышь")

    def _apply_deadzone(self, value: float) -> float:
        """Применение мёртвой зоны к значению оси"""
        if abs(value) < self.DEADZONE:
            return 0.0
        # Нормализация значения после deadzone
        sign = 1 if value > 0 else -1
        return sign * (abs(value) - self.DEADZONE) / (1.0 - self.DEADZONE)

    def update(self, events: list, dt: float):
        """Обновление состояния ввода"""
        # Сброс состояний "just pressed/released"
        for btn_state in self.state.buttons.values():
            btn_state.pressed = False
            btn_state.released = False

        self.state.keys_just_pressed.clear()
        self.state.keys_just_released.clear()
        self.state.mouse_just_pressed.clear()
        self.state.dpad_pressed = {}

        # Обработка событий pygame
        for event in events:
            self._process_event(event)

        # Обновление состояния джойстика
        if self.joystick:
            self._update_joystick(dt)

        # Обновление состояния клавиатуры
        self._update_keyboard()

        # Обновление модификаторов
        self._update_modifiers()

    def _process_event(self, event):
        """Обработка отдельного события"""
        # События мыши/тачскрина
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.state.mouse_buttons[event.button] = True
            self.state.mouse_just_pressed.add(event.button)
        elif event.type == pygame.MOUSEBUTTONUP:
            self.state.mouse_buttons[event.button] = False
        elif event.type == pygame.MOUSEMOTION:
            self.state.mouse_pos = event.pos

        # События мультитача
        elif event.type == pygame.FINGERDOWN:
            finger_id = event.finger_id
            x = int(event.x * pygame.display.get_surface().get_width())
            y = int(event.y * pygame.display.get_surface().get_height())
            self.state.touch_points[finger_id] = (x, y)
        elif event.type == pygame.FINGERUP:
            if event.finger_id in self.state.touch_points:
                del self.state.touch_points[event.finger_id]
        elif event.type == pygame.FINGERMOTION:
            finger_id = event.finger_id
            x = int(event.x * pygame.display.get_surface().get_width())
            y = int(event.y * pygame.display.get_surface().get_height())
            self.state.touch_points[finger_id] = (x, y)

        # Подключение/отключение джойстика
        elif event.type == pygame.JOYDEVICEADDED:
            self._init_joystick()
        elif event.type == pygame.JOYDEVICEREMOVED:
            self.joystick = None
            print("Контроллер отключён")

    def _update_joystick(self, dt: float):
        """Обновление состояния джойстика"""
        # Кнопки
        for btn in range(self.joystick.get_numbuttons()):
            current = self.joystick.get_button(btn)
            prev = self._prev_buttons.get(btn, False)

            if btn not in self.state.buttons:
                self.state.buttons[btn] = ButtonState()

            btn_state = self.state.buttons[btn]

            if current and not prev:
                btn_state.pressed = True
                btn_state.held = True
                btn_state.hold_time = 0.0
            elif not current and prev:
                btn_state.released = True
                btn_state.held = False
                btn_state.hold_time = 0.0
            elif current:
                btn_state.hold_time += dt

            self._prev_buttons[btn] = current

        # D-Pad (HAT)
        if self.joystick.get_numhats() > 0:
            hat = self.joystick.get_hat(0)
            self.state.dpad = hat

            # Определяем "just pressed" для D-Pad
            if hat[0] == -1 and self._prev_dpad[0] != -1:
                self.state.dpad_pressed["left"] = True
            if hat[0] == 1 and self._prev_dpad[0] != 1:
                self.state.dpad_pressed["right"] = True
            if hat[1] == 1 and self._prev_dpad[1] != 1:
                self.state.dpad_pressed["up"] = True
            if hat[1] == -1 and self._prev_dpad[1] != -1:
                self.state.dpad_pressed["down"] = True

            self._prev_dpad = hat

        # Аналоговые стики
        if self.joystick.get_numaxes() >= 2:
            self.state.left_stick = (
                self._apply_deadzone(self.joystick.get_axis(ControllerAxes.LEFT_X)),
                self._apply_deadzone(self.joystick.get_axis(ControllerAxes.LEFT_Y))
            )

        if self.joystick.get_numaxes() >= 4:
            self.state.right_stick = (
                self._apply_deadzone(self.joystick.get_axis(ControllerAxes.RIGHT_X)),
                self._apply_deadzone(self.joystick.get_axis(ControllerAxes.RIGHT_Y))
            )

        # Триггеры
        if self.joystick.get_numaxes() >= 6:
            # Триггеры обычно от -1 (отпущен) до 1 (нажат), нормализуем в 0-1
            self.state.left_trigger = (self.joystick.get_axis(ControllerAxes.L2) + 1) / 2
            self.state.right_trigger = (self.joystick.get_axis(ControllerAxes.R2) + 1) / 2

    def _update_keyboard(self):
        """Обновление состояния клавиатуры"""
        keys = pygame.key.get_pressed()
        current_keys = {k for k in range(len(keys)) if keys[k]}

        self.state.keys_just_pressed = current_keys - self._prev_keys
        self.state.keys_just_released = self._prev_keys - current_keys
        self.state.keys_pressed = current_keys

        self._prev_keys = current_keys

    def _update_modifiers(self):
        """Обновление активных модификаторов"""
        self.state.active_modifiers.clear()

        for btn in self.MODIFIER_BUTTONS:
            if btn in self.state.buttons:
                btn_state = self.state.buttons[btn]
                if btn_state.held and btn_state.hold_time >= MODIFIER_HOLD_TIME:
                    self.state.active_modifiers.add(btn)

    # === Удобные методы для проверки состояния ===

    def is_button_pressed(self, button: int) -> bool:
        """Кнопка только что нажата"""
        return self.state.buttons.get(button, ButtonState()).pressed

    def is_button_held(self, button: int) -> bool:
        """Кнопка удерживается"""
        return self.state.buttons.get(button, ButtonState()).held

    def is_button_released(self, button: int) -> bool:
        """Кнопка только что отпущена"""
        return self.state.buttons.get(button, ButtonState()).released

    def is_modifier_active(self, button: int) -> bool:
        """Модификатор активен (кнопка зажата достаточно долго)"""
        return button in self.state.active_modifiers

    def is_dpad_pressed(self, direction: str) -> bool:
        """D-Pad только что нажат в направлении (left/right/up/down)"""
        return self.state.dpad_pressed.get(direction, False)

    def is_key_pressed(self, key: int) -> bool:
        """Клавиша только что нажата"""
        return key in self.state.keys_just_pressed

    def is_key_held(self, key: int) -> bool:
        """Клавиша удерживается"""
        return key in self.state.keys_pressed

    def is_mouse_pressed(self, button: int = 1) -> bool:
        """Кнопка мыши только что нажата"""
        return self.state.mouse_buttons.get(button, False)

    def get_mouse_pos(self) -> Tuple[int, int]:
        """Позиция мыши"""
        return self.state.mouse_pos

    def get_touch_points(self) -> Dict[int, Tuple[int, int]]:
        """Все активные точки касания"""
        return self.state.touch_points.copy()

    def is_escape_pressed(self) -> bool:
        """Проверка нажатия ESC/Start для выхода"""
        return (
            self.is_key_pressed(pygame.K_ESCAPE) or
            self.is_button_pressed(ControllerButtons.START)
        )

    def is_option_pressed(self) -> bool:
        """Проверка нажатия кнопки Options/Select"""
        return (
            self.is_key_pressed(pygame.K_F11) or
            self.is_button_pressed(ControllerButtons.SELECT)
        )

