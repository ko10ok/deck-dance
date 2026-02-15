"""
Менеджер сцен - загрузка, переключение и управление сценами
"""

import os
from typing import List, Optional
from src.config import SCENES_DIR
from src.scenes.base_scene import Scene
from src.scenes.scene_loader import SceneLoader
from src.animations.animation_registry import AnimationRegistry, register_all_animations


class SceneManager:
    """Менеджер для загрузки и переключения между сценами"""

    def __init__(self):
        self.scenes: List[Scene] = []
        self.current_index: int = 0
        self.loader = SceneLoader()

        # Регистрируем все анимации
        register_all_animations()

        # Получаем список доступных анимаций
        self.available_animations = AnimationRegistry.get_all_names()

        # Загрузка сцен из директории
        self._load_scenes()

        # Создаём дефолтную сцену если нет других
        if not self.scenes:
            self._create_default_scene()

    def _load_scenes(self):
        """Загрузка всех сцен из директории"""
        if not os.path.exists(SCENES_DIR):
            os.makedirs(SCENES_DIR)
            return

        for filename in sorted(os.listdir(SCENES_DIR)):
            if filename.endswith('.json'):
                filepath = os.path.join(SCENES_DIR, filename)
                scene = self.loader.load(filepath, self.available_animations)
                if scene:
                    self.scenes.append(scene)

    def _create_default_scene(self):
        """Создание дефолтной сцены"""
        # Получаем дефолтные конфигурации из реестра
        default_configs = AnimationRegistry.get_all_default_configs()

        default_scene = Scene(
            name="Default Scene",
            background_color=(0.1, 0.1, 0.15, 1.0),
            animation_configs=default_configs,
            available_animations=self.available_animations.copy(),
            current_animation_index=0
        )
        self.scenes.append(default_scene)

        # Сохраняем дефолтную сцену
        self._save_default_scene(default_scene)

    def _save_default_scene(self, scene: Scene):
        """Сохранение дефолтной сцены"""
        if not os.path.exists(SCENES_DIR):
            os.makedirs(SCENES_DIR)

        filepath = os.path.join(SCENES_DIR, "default.json")
        self.loader.save(scene, filepath)

    @property
    def current_scene(self) -> Optional[Scene]:
        """Текущая активная сцена"""
        if self.scenes and 0 <= self.current_index < len(self.scenes):
            return self.scenes[self.current_index]
        return None

    def next_scene(self):
        """Переключение на следующую сцену"""
        if self.scenes:
            self.current_index = (self.current_index + 1) % len(self.scenes)

    def prev_scene(self):
        """Переключение на предыдущую сцену"""
        if self.scenes:
            self.current_index = (self.current_index - 1) % len(self.scenes)

    def select_scene(self, index: int):
        """Выбор сцены по индексу"""
        if 0 <= index < len(self.scenes):
            self.current_index = index

    def get_scene_names(self) -> List[str]:
        """Получение списка имён всех сцен"""
        return [scene.name for scene in self.scenes]

    def add_scene(self, scene: Scene):
        """Добавление новой сцены"""
        self.scenes.append(scene)

    def remove_scene(self, index: int):
        """Удаление сцены по индексу"""
        if 0 <= index < len(self.scenes) and len(self.scenes) > 1:
            del self.scenes[index]
            if self.current_index >= len(self.scenes):
                self.current_index = len(self.scenes) - 1

    def reload_scenes(self):
        """Перезагрузка всех сцен с диска"""
        self.scenes.clear()
        self.current_index = 0
        self._load_scenes()
        if not self.scenes:
            self._create_default_scene()

