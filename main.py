"""
Steam Deck Multimedia Application
Точка входа приложения
"""

import sys
import os

# Добавляем src в путь
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.app import App


def main():
    app = App()
    app.run()


if __name__ == "__main__":
    main()

