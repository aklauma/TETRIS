"""
Цвета и стили интерфейса.

Как изменить оформление:
1. Поменяйте значения в COLORS (hex-цвета).
2. При необходимости отредактируйте STYLE_SHEET ниже.
3. Перезапустите игру: python main.py

В Qt Designer можно задать styleSheet отдельному виджету
(свойство styleSheet в Inspector) — он перекроет глобальные правила.
"""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLabel, QWidget

# --- Палитра (меняйте здесь) ---
COLORS = {
    "bg_main": "#1a1a2e",       # фон окна
    "bg_panel": "#16213e",      # панели, рамки, кнопки
    "bg_panel_hover": "#0f3460",
    "border": "#0f3460",
    "accent": "#e94560",        # акцент (hover, заголовки)
    "text": "#e0e0e0",
    "text_muted": "#a0a0c0",
    "board": "#0a0a1e",         # фон игрового поля (в game_widgets.py)
}

STYLE_SHEET = f"""
QMainWindow {{
    background-color: {COLORS["bg_main"]};
}}
QWidget {{
    background-color: {COLORS["bg_main"]};
    color: {COLORS["text"]};
}}
QLabel {{
    background: transparent;
    background-color: transparent;
    color: {COLORS["text"]};
    border: none;
}}
QPushButton {{
    background-color: {COLORS["bg_panel"]};
    color: {COLORS["text"]};
    border: 2px solid {COLORS["border"]};
    border-radius: 8px;
    padding: 6px 16px;
    font-weight: bold;
}}
QPushButton:hover {{
    background-color: {COLORS["bg_panel_hover"]};
    border-color: {COLORS["accent"]};
}}
QPushButton:pressed {{
    background-color: {COLORS["accent"]};
}}
QGroupBox {{
    color: {COLORS["text"]};
    background-color: {COLORS["bg_panel"]};
    border: 1px solid {COLORS["border"]};
    border-radius: 6px;
    margin-top: 10px;
    padding: 8px;
}}
QFrame#frame_game_field, QFrame#frame_next_preview {{
    background-color: {COLORS["bg_panel"]};
    border: 2px solid {COLORS["border"]};
}}
"""


def apply_transparent_text(widget: QWidget) -> None:
    """Убирает непрозрачный фон у всех подписей на экране."""
    widget.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
    for label in widget.findChildren(QLabel):
        label.setAutoFillBackground(False)
