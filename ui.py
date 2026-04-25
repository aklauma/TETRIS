from PyQt6.QtCore import QRect, Qt, QTimer
from PyQt6.QtGui import QColor, QPainter, QPen
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from tetris_game import (
    BOARD_HEIGHT,
    BOARD_WIDTH,
    CELL_SIZE,
    PIECE_COLORS,
    SHAPES,
)


class BoardWidget(QWidget):
    def __init__(self, game, parent=None):
        super().__init__(parent)
        self.game = game
        self.setMinimumSize(220, 420)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)
        painter.fillRect(self.rect(), QColor(10, 10, 30))

        cell_size = max(8, min((self.width() - 1) // BOARD_WIDTH, (self.height() - 1) // BOARD_HEIGHT))
        board_px_w = cell_size * BOARD_WIDTH
        board_px_h = cell_size * BOARD_HEIGHT
        offset_x = (self.width() - board_px_w) // 2
        offset_y = (self.height() - board_px_h) // 2

        painter.setPen(QPen(QColor(30, 30, 60), 1))
        for x in range(BOARD_WIDTH + 1):
            px = offset_x + x * cell_size
            painter.drawLine(px, offset_y, px, offset_y + board_px_h)
        for y in range(BOARD_HEIGHT + 1):
            py = offset_y + y * cell_size
            painter.drawLine(offset_x, py, offset_x + board_px_w, py)

        for y in range(BOARD_HEIGHT):
            for x in range(BOARD_WIDTH):
                if self.game.board[y][x] is not None:
                    self._draw_cell(painter, x, y, self.game.board[y][x], cell_size, offset_x, offset_y)

        if self.game.current_piece and not self.game.game_over:
            ghost_y = self.game.get_ghost_y()
            shape = SHAPES[self.game.current_piece][self.game.rotation]
            color = PIECE_COLORS[self.game.current_piece]
            ghost_color = QColor(color.red(), color.green(), color.blue(), 50)
            for dx, dy in shape:
                bx = self.game.piece_x + dx
                by = ghost_y + dy
                if 0 <= bx < BOARD_WIDTH and 0 <= by < BOARD_HEIGHT:
                    self._draw_cell(
                        painter, bx, by, ghost_color, cell_size, offset_x, offset_y, is_ghost=True
                    )

        if self.game.current_piece and not self.game.game_over:
            shape = SHAPES[self.game.current_piece][self.game.rotation]
            color = PIECE_COLORS[self.game.current_piece]
            for dx, dy in shape:
                bx = self.game.piece_x + dx
                by = self.game.piece_y + dy
                if 0 <= bx < BOARD_WIDTH and 0 <= by < BOARD_HEIGHT:
                    self._draw_cell(painter, bx, by, color, cell_size, offset_x, offset_y)

    def _draw_cell(self, painter, x, y, color, cell_size, offset_x, offset_y, is_ghost=False):
        rect = QRect(
            offset_x + x * cell_size + 1,
            offset_y + y * cell_size + 1,
            cell_size - 1,
            cell_size - 1,
        )
        if is_ghost:
            painter.fillRect(rect, color)
            painter.setPen(QPen(QColor(color.red(), color.green(), color.blue(), 80), 1))
            painter.drawRect(rect)
            return

        painter.fillRect(rect, color)
        lighter = QColor(
            min(255, color.red() + 60),
            min(255, color.green() + 60),
            min(255, color.blue() + 60),
        )
        painter.setPen(QPen(lighter, 1))
        painter.drawLine(rect.left(), rect.top(), rect.right(), rect.top())
        painter.drawLine(rect.left(), rect.top(), rect.left(), rect.bottom())

        darker = QColor(
            max(0, color.red() - 60),
            max(0, color.green() - 60),
            max(0, color.blue() - 60),
        )
        painter.setPen(QPen(darker, 1))
        painter.drawLine(rect.right(), rect.top(), rect.right(), rect.bottom())
        painter.drawLine(rect.left(), rect.bottom(), rect.right(), rect.bottom())


class NextPieceWidget(QWidget):
    def __init__(self, game, parent=None):
        super().__init__(parent)
        self.game = game
        self.setMinimumSize(90, 90)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(10, 10, 30))
        painter.setPen(QPen(QColor(50, 50, 80), 2))
        painter.drawRect(0, 0, self.width() - 1, self.height() - 1)

        if not self.game.next_piece:
            return

        inner_margin = 6
        inner_w = max(20, self.width() - inner_margin * 2)
        inner_h = max(20, self.height() - inner_margin * 2)
        cell_size = max(6, min(inner_w // 5, inner_h // 5))
        board_px = cell_size * 5
        base_x = inner_margin + (inner_w - board_px) // 2
        base_y = inner_margin + (inner_h - board_px) // 2
        painter.setClipRect(inner_margin, inner_margin, inner_w, inner_h)

        shape = SHAPES[self.game.next_piece][0]
        color = PIECE_COLORS[self.game.next_piece]
        xs = [coord[0] for coord in shape]
        ys = [coord[1] for coord in shape]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        width = max_x - min_x + 1
        height = max_y - min_y + 1
        offset_x = (5 - width) / 2 - min_x
        offset_y = (5 - height) / 2 - min_y

        for dx, dy in shape:
            px = base_x + int((dx + offset_x) * cell_size) + 1
            py = base_y + int((dy + offset_y) * cell_size) + 1
            rect = QRect(px, py, cell_size - 1, cell_size - 1)
            painter.fillRect(rect, color)

            lighter = QColor(
                min(255, color.red() + 60),
                min(255, color.green() + 60),
                min(255, color.blue() + 60),
            )
            painter.setPen(QPen(lighter, 1))
            painter.drawLine(rect.left(), rect.top(), rect.right(), rect.top())
            painter.drawLine(rect.left(), rect.top(), rect.left(), rect.bottom())

            darker = QColor(
                max(0, color.red() - 60),
                max(0, color.green() - 60),
                max(0, color.blue() - 60),
            )
            painter.setPen(QPen(darker, 1))
            painter.drawLine(rect.right(), rect.top(), rect.right(), rect.bottom())
            painter.drawLine(rect.left(), rect.bottom(), rect.right(), rect.bottom())


class MainMenuWidget(QWidget):
    def __init__(self, on_play, on_rules, on_exit, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(20)

        title = QLabel("Тетрис")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(
            "font-size: 48px; font-weight: bold; color: #e94560; margin-bottom: 30px;"
        )
        layout.addWidget(title)

        subtitle = QLabel("Главное меню")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet(
            "font-size: 20px; color: #a0a0c0; margin-bottom: 20px;"
        )
        layout.addWidget(subtitle)

        btn_play = QPushButton("Играть")
        btn_play.clicked.connect(on_play)
        btn_play.setStyleSheet(
            """
            QPushButton {
                background-color: #0f3460;
                color: #e0e0e0;
                border: 2px solid #e94560;
                border-radius: 8px;
                padding: 14px 24px;
                font-size: 18px;
                font-weight: bold;
                min-width: 220px;
            }
            QPushButton:hover { background-color: #e94560; }
            """
        )
        layout.addWidget(btn_play, alignment=Qt.AlignmentFlag.AlignCenter)

        btn_rules = QPushButton("Правила")
        btn_rules.clicked.connect(on_rules)
        layout.addWidget(btn_rules, alignment=Qt.AlignmentFlag.AlignCenter)

        btn_exit = QPushButton("Выход")
        btn_exit.clicked.connect(on_exit)
        layout.addWidget(btn_exit, alignment=Qt.AlignmentFlag.AlignCenter)


class RulesWidget(QWidget):
    def __init__(self, on_back, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(15)

        title = QLabel("Правила и управление")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(
            "font-size: 28px; font-weight: bold; color: #e94560; margin-bottom: 10px;"
        )
        layout.addWidget(title)

        columns_layout = QHBoxLayout()
        columns_layout.setSpacing(40)

        rules_frame = QFrame()
        rules_frame.setStyleSheet(
            """
            QFrame {
                background-color: #16213e;
                border: 1px solid #0f3460;
                border-radius: 8px;
                padding: 15px;
            }
            """
        )
        rules_layout = QVBoxLayout(rules_frame)
        rules_title = QLabel("Правила")
        rules_title.setStyleSheet(
            "font-size: 20px; font-weight: bold; color: #e94560; margin-bottom: 5px;"
        )
        rules_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        rules_layout.addWidget(rules_title)
        rules_text = QLabel(
            "• Фигуры падают сверху вниз\n"
            "• Заполните горизонтальную\n"
            "  линию полностью для её удаления\n"
            "• Каждые 10 линий — новый уровень\n"
            "• Скорость растёт с уровнем\n"
            "• Игра окончена, когда фигуры\n"
            "  достигнут верха поля\n\n"
            "Очки за линии (×(Уровень+1)):\n"
            "  1 линия  — 40 очков\n"
            "  2 линии  — 100 очков\n"
            "  3 линии  — 300 очков\n"
            "  4 линии  — 1200 очков\n\n"
            "Soft Drop: +1 за клетку\n"
            "Hard Drop: +2 за клетку"
        )
        rules_text.setStyleSheet("font-size: 13px; color: #c0c0e0;")
        rules_text.setWordWrap(True)
        rules_layout.addWidget(rules_text)
        columns_layout.addWidget(rules_frame)

        controls_frame = QFrame()
        controls_frame.setStyleSheet(
            """
            QFrame {
                background-color: #16213e;
                border: 1px solid #0f3460;
                border-radius: 8px;
                padding: 15px;
            }
            """
        )
        controls_layout = QVBoxLayout(controls_frame)
        controls_title = QLabel("Управление")
        controls_title.setStyleSheet(
            "font-size: 20px; font-weight: bold; color: #e94560; margin-bottom: 5px;"
        )
        controls_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        controls_layout.addWidget(controls_title)
        controls_text = QLabel(
            "← / A — Движение влево\n\n"
            "→ / D — Движение вправо\n\n"
            "↑ / W — Поворот фигуры\n\n"
            "↓ / S — Soft Drop\n"
            "  (мягкое падение)\n\n"
            "Пробел — Hard Drop\n"
            "  (жёсткое падение)\n\n"
            "P — Пауза"
        )
        controls_text.setStyleSheet("font-size: 13px; color: #c0c0e0;")
        controls_text.setWordWrap(True)
        controls_layout.addWidget(controls_text)
        columns_layout.addWidget(controls_frame)

        layout.addLayout(columns_layout)

        btn_back = QPushButton("Главное меню")
        btn_back.clicked.connect(on_back)
        layout.addWidget(btn_back, alignment=Qt.AlignmentFlag.AlignCenter)


class GameOverWidget(QWidget):
    def __init__(self, on_menu, on_exit, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(20)

        title = QLabel("Конец игры")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(
            "font-size: 36px; font-weight: bold; color: #e94560; margin-bottom: 10px;"
        )
        layout.addWidget(title)

        result_frame = QFrame()
        result_frame.setStyleSheet(
            """
            QFrame {
                background-color: #16213e;
                border: 2px solid #0f3460;
                border-radius: 10px;
                padding: 20px;
            }
            """
        )
        result_layout = QVBoxLayout(result_frame)
        self.score_label = QLabel("Кол-во очков: 0")
        self.score_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.score_label.setStyleSheet(
            "font-size: 22px; font-weight: bold; color: #e0e0e0;"
        )
        result_layout.addWidget(self.score_label)
        self.level_label = QLabel("Уровень: 0")
        self.level_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.level_label.setStyleSheet(
            "font-size: 22px; font-weight: bold; color: #a0a0c0;"
        )
        result_layout.addWidget(self.level_label)
        layout.addWidget(result_frame, alignment=Qt.AlignmentFlag.AlignCenter)

        btn_menu = QPushButton("Главное меню")
        btn_menu.clicked.connect(on_menu)
        layout.addWidget(btn_menu, alignment=Qt.AlignmentFlag.AlignCenter)

        btn_exit = QPushButton("Выход")
        btn_exit.clicked.connect(on_exit)
        layout.addWidget(btn_exit, alignment=Qt.AlignmentFlag.AlignCenter)

    def set_results(self, score, level):
        self.score_label.setText(f"Кол-во очков: {score}")
        self.level_label.setText(f"Уровень: {level}")


class GameWidget(QWidget):
    def __init__(self, game, on_game_over, parent=None):
        super().__init__(parent)
        self.game = game
        self.on_game_over = on_game_over
        self.paused = False
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        main_layout = QHBoxLayout(self)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.setSpacing(20)
        self._main_layout = main_layout

        self.board_widget = BoardWidget(game)
        main_layout.addWidget(self.board_widget, 3)

        right_panel = QVBoxLayout()
        right_panel.setSpacing(15)
        right_panel.setAlignment(Qt.AlignmentFlag.AlignTop)
        self._right_panel = right_panel

        score_frame = QFrame()
        score_frame.setStyleSheet(
            """
            QFrame {
                background-color: #16213e;
                border: 1px solid #0f3460;
                border-radius: 6px;
                padding: 10px;
            }
            """
        )
        score_layout = QVBoxLayout(score_frame)
        score_title = QLabel("Счёт")
        score_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        score_title.setStyleSheet("font-size: 14px; color: #a0a0c0;")
        score_layout.addWidget(score_title)
        self.score_value = QLabel("0")
        self.score_value.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.score_value.setStyleSheet("font-size: 22px; font-weight: bold; color: #e94560;")
        score_layout.addWidget(self.score_value)
        level_title = QLabel("Уровень")
        level_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        level_title.setStyleSheet("font-size: 14px; color: #a0a0c0;")
        score_layout.addWidget(level_title)
        self.level_value = QLabel("0")
        self.level_value.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.level_value.setStyleSheet("font-size: 22px; font-weight: bold; color: #0f3460;")
        score_layout.addWidget(self.level_value)
        right_panel.addWidget(score_frame)

        next_frame = QFrame()
        self.next_frame = next_frame
        next_frame.setStyleSheet(
            """
            QFrame {
                background-color: #16213e;
                border: 1px solid #0f3460;
                border-radius: 6px;
                padding: 10px;
            }
            """
        )
        next_layout = QVBoxLayout(next_frame)
        next_title = QLabel("Следующая\nфигура")
        next_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        next_title.setStyleSheet("font-size: 14px; color: #a0a0c0;")
        next_layout.addWidget(next_title)
        self.next_piece_widget = NextPieceWidget(game)
        next_layout.addWidget(self.next_piece_widget, alignment=Qt.AlignmentFlag.AlignCenter)
        right_panel.addWidget(next_frame)

        controls_frame = QFrame()
        controls_frame.setStyleSheet(
            """
            QFrame {
                background-color: #16213e;
                border: 1px solid #0f3460;
                border-radius: 6px;
                padding: 10px;
            }
            """
        )
        controls_layout = QVBoxLayout(controls_frame)
        controls_title = QLabel("Управление")
        controls_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        controls_title.setStyleSheet("font-size: 14px; color: #a0a0c0; margin-bottom: 5px;")
        controls_layout.addWidget(controls_title)
        controls_text = QLabel(
            "← → — Движение\n"
            "↑ — Поворот\n"
            "↓ — Soft Drop\n"
            "Пробел — Hard Drop\n"
            "P — Пауза"
        )
        controls_text.setStyleSheet("font-size: 12px; color: #808090;")
        controls_layout.addWidget(controls_text)
        right_panel.addWidget(controls_frame)

        self.pause_label = QLabel("")
        self.pause_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.pause_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #e94560;")
        right_panel.addWidget(self.pause_label)

        right_panel_widget = QWidget()
        right_panel_widget.setLayout(right_panel)
        right_panel_widget.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        self.right_panel_widget = right_panel_widget
        main_layout.addWidget(self.right_panel_widget, 2)

        self.timer = QTimer()
        self.timer.timeout.connect(self._tick)
        self._apply_scaling()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._apply_scaling()

    def _apply_scaling(self):
        panel_width = self.right_panel_widget.width() or max(220, self.width() // 3)
        side_by_width = int(panel_width * 0.55)
        side_by_height = int(self.height() * 0.24)
        side = max(90, min(side_by_width, side_by_height, 170))
        self.next_piece_widget.setMinimumSize(side, side)
        self.next_piece_widget.setMaximumSize(side, side)

        panel_width = max(220, self.width() // 3)
        self.right_panel_widget.setMinimumWidth(panel_width // 2)
        self.right_panel_widget.setMaximumWidth(panel_width)

    def start_game(self):
        self.game.reset()
        self.paused = False
        self.pause_label.setText("")
        self._update_display()
        self.timer.start(self.game.get_fall_interval())
        self.setFocus()

    def _tick(self):
        if not self.paused and not self.game.game_over:
            self.game.tick()
            self._update_display()
            if self.game.game_over:
                self.timer.stop()
                self.on_game_over(self.game.score, self.game.level)

    def _update_display(self):
        self.score_value.setText(str(self.game.score))
        self.level_value.setText(str(self.game.level))
        self.board_widget.update()
        self.next_piece_widget.update()
        interval = self.game.get_fall_interval()
        if self.timer.interval() != interval:
            self.timer.setInterval(interval)

    def keyPressEvent(self, event):
        key = event.key()
        text = event.text().lower()
        if key == Qt.Key.Key_P or text == "з":
            self._toggle_pause()
            return

        if self.paused or self.game.game_over:
            return

        if key in (Qt.Key.Key_Left, Qt.Key.Key_A) or text == "ф":
            self.game.move_left()
        elif key in (Qt.Key.Key_Right, Qt.Key.Key_D) or text == "в":
            self.game.move_right()
        elif key in (Qt.Key.Key_Up, Qt.Key.Key_W) or text == "ц":
            self.game.rotate()
        elif key in (Qt.Key.Key_Down, Qt.Key.Key_S, Qt.Key.Key_Space) or text == "ы":
            self.game.soft_drop()
        elif key in (Qt.Key.Key_Enter, Qt.Key.Key_Return):
            self.game.hard_drop()
            if self.game.game_over:
                self.timer.stop()
                self.on_game_over(self.game.score, self.game.level)
        else:
            super().keyPressEvent(event)
            return

        self._update_display()

    def _toggle_pause(self):
        if self.game.game_over:
            return
        self.paused = not self.paused
        if self.paused:
            self.timer.stop()
            self.pause_label.setText("ПАУЗА")
        else:
            self.timer.start(self.game.get_fall_interval())
            self.pause_label.setText("")
