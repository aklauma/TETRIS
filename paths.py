"""Пути к ресурсам (обычный запуск и PyInstaller exe)."""

import sys
from pathlib import Path


def app_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parent


UI_DIR = app_dir() / "Interface"
FONTS_DIR = app_dir() / "fonts"


def load_bundled_font() -> str | None:
    """
    Подключает шрифты из папки fonts/ (для exe и локального запуска).
    Положите сюда файл, например: Expressway Free.ttf
    """
    from PyQt6.QtGui import QFontDatabase

    if not FONTS_DIR.is_dir():
        return None

    family = None
    for pattern in ("*.ttf", "*.otf", "*.TTF", "*.OTF"):
        for font_path in sorted(FONTS_DIR.glob(pattern)):
            font_id = QFontDatabase.addApplicationFont(str(font_path))
            if font_id < 0:
                continue
            families = QFontDatabase.applicationFontFamilies(font_id)
            if families:
                family = families[0]
    return family
