# Steam Deck Multimedia Application

Мультимедиа приложение для Steam Deck с поддержкой контроллера, 3D рендеринга и анимаций.

## Требования

- Python 3.10+
- OpenGL 3.3+
- Steam Deck / Linux / Windows

## Быстрый старт (Linux/Steam Deck)

```bash
chmod +x start.sh
./start.sh
```

Скрипт автоматически:
1. Создаст виртуальное окружение `.venv`
2. Установит зависимости из `requirements.txt`
3. Запустит приложение

## Быстрый старт (Windows)

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

## Управление

### Главное меню
- **↑↓ / D-Pad** - навигация
- **A / Enter** - выбор
- **Start / ESC** - выход

### Режим воспроизведения
- **Клик / A** - создать анимацию
- **←→ / D-Pad** - смена сцены
- **Зажать X** - меню выбора сцен
- **Select / F11** - переключить полноэкранный режим
- **Start / ESC** - выход в меню

### Режим редактора
- **↑↓ / D-Pad** - навигация
- **A / Enter** - действие
- **Start / ESC** - выход в меню

## Структура проекта

```
SDeckMMedia/
├── start.sh                    # Скрипт запуска для Linux
├── requirements.txt            # Python зависимости
├── main.py                     # Точка входа
├── src/
│   ├── app.py                  # Главный класс приложения
│   ├── config.py               # Настройки
│   ├── core/
│   │   ├── input_manager.py    # Обработка ввода (контроллер + модификаторы)
│   │   ├── renderer.py         # ModernGL рендеринг
│   │   └── scene_manager.py    # Управление сценами
│   ├── screens/
│   │   ├── base_screen.py      # Базовый класс экрана
│   │   ├── main_menu.py        # Главное меню
│   │   ├── playback_screen.py  # Режим воспроизведения
│   │   └── editor_screen.py    # Редактор сцен
│   ├── animations/
│   │   ├── base_animation.py   # Базовый класс анимации
│   │   ├── expanding_circle.py # Расходящийся круг
│   │   └── animation_pool.py   # Пул анимаций
│   ├── scenes/
│   │   ├── base_scene.py       # Класс сцены
│   │   └── scene_loader.py     # Загрузчик сцен
│   └── ui/
│       └── scene_picker.py     # Меню выбора сцен
└── assets/
    ├── shaders/                # GLSL шейдеры
    └── scenes/                 # JSON файлы сцен
```

## Расширение

### Добавление новой анимации

1. Создайте файл в `src/animations/`:

```python
from src.animations.base_animation import BaseAnimation

class MyAnimation(BaseAnimation):
    def __init__(self, center, duration=1.0, **kwargs):
        super().__init__(center, duration, **kwargs)
        # Инициализация параметров
    
    def _update(self, dt):
        # Обновление состояния
        pass
    
    def render(self, renderer):
        # Отрисовка
        pass
```

2. Добавьте конфигурацию в сцену (JSON):

```json
{
  "animation_configs": {
    "my_animation": {
      "param1": "value1"
    }
  }
}
```

### Добавление новой сцены

Создайте JSON файл в `assets/scenes/`:

```json
{
  "name": "My Scene",
  "background_color": [0.1, 0.1, 0.15, 1.0],
  "animation_configs": {
    "expanding_circle": {
      "color": [1.0, 0.5, 0.0, 1.0],
      "duration": 1.5,
      "max_radius": 200.0,
      "ring_width": 0.1
    }
  }
}
```

## Технологии

- **pygame** - окно, ввод, SDL интеграция
- **ModernGL** - современный OpenGL 3.3 рендеринг
- **pyrr** - математика для 3D (матрицы, векторы)
- **numpy** - числовые операции

## Лицензия

MIT

