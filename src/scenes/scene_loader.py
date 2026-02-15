"""
Загрузчик сцен из файлов
"""

import json
import os
from typing import Optional, List
from src.scenes.base_scene import Scene


class SceneLoader:
    """Загрузчик и сохранение сцен в формате JSON"""

    def load(self, filepath: str, available_animations: List[str] = None) -> Optional[Scene]:
        """Загрузка сцены из файла"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return Scene.from_dict(data, available_animations)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Ошибка загрузки сцены {filepath}: {e}")
            return None

    def save(self, scene: Scene, filepath: str) -> bool:
        """Сохранение сцены в файл"""
        try:
            # Создаём директорию если её нет
            os.makedirs(os.path.dirname(filepath), exist_ok=True)

            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(scene.to_dict(), f, indent=2, ensure_ascii=False)
            return True
        except IOError as e:
            print(f"Ошибка сохранения сцены {filepath}: {e}")
            return False

    def load_all_from_directory(self, directory: str, available_animations: List[str] = None) -> list:
        """Загрузка всех сцен из директории"""
        scenes = []

        if not os.path.exists(directory):
            return scenes

        for filename in sorted(os.listdir(directory)):
            if filename.endswith('.json'):
                filepath = os.path.join(directory, filename)
                scene = self.load(filepath, available_animations)
                if scene:
                    scenes.append(scene)

        return scenes

