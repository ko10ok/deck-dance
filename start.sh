#!/bin/bash

# Steam Deck Multimedia Application Launcher
# Автоматическая установка venv и запуск приложения

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

VENV_DIR=".venv"
PYTHON_CMD="python3"
REQUIREMENTS_FILE="requirements.txt"

echo "=== Steam Deck Multimedia App ==="

# Проверка наличия Python
if ! command -v $PYTHON_CMD &> /dev/null; then
    echo "Python3 не найден. Установите Python3."
    exit 1
fi

# Создание виртуального окружения если его нет
if [ ! -d "$VENV_DIR" ]; then
    echo "Создание виртуального окружения..."
    $PYTHON_CMD -m venv "$VENV_DIR"
    if [ $? -ne 0 ]; then
        echo "Ошибка создания виртуального окружения"
        exit 1
    fi
fi

# Активация venv
echo "Активация виртуального окружения..."
source "$VENV_DIR/bin/activate"

# Установка/обновление зависимостей
if [ -f "$REQUIREMENTS_FILE" ]; then
    echo "Установка зависимостей..."
    pip install -r "$REQUIREMENTS_FILE" --quiet --upgrade
    if [ $? -ne 0 ]; then
        echo "Ошибка установки зависимостей"
        exit 1
    fi
fi

# Запуск приложения
echo "Запуск приложения..."
$PYTHON_CMD main.py "$@"

# Деактивация venv при выходе
deactivate

