from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QDialog, QMessageBox)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QPainter, QColor, QFont, QKeyEvent
from tetris_game import TetrisGame

class GameBoardWidget(QWidget):
    """Виджет игрового поля"""
    
    def __init__(self, game, parent=None):
        super().__init__(parent)
        self.game = game
    
    def paintEvent(self, event):
        """Отрисовка игрового поля"""
        painter = QPainter(self)
        cell_size = 30
        board = self.game.get_board()
        
        for y in range(TetrisGame.BOARD_HEIGHT):
            for x in range(TetrisGame.BOARD_WIDTH):
                cell_x = x * cell_size
                cell_y = y * cell_size
                
                if board[y][x]:
                    color_index = board[y][x] - 1
                    color = TetrisGame.COLORS[color_index]
                    painter.fillRect(cell_x, cell_y, cell_size - 1, cell_size - 1, color)
                else:
                    painter.fillRect(cell_x, cell_y, cell_size - 1, cell_size - 1, QColor(20, 20, 20))


class NextPieceWidget(QWidget):
    """Виджет следующей фигуры"""
    
    def __init__(self, game, parent=None):
        super().__init__(parent)
        self.game = game
    
    def paintEvent(self, event):
        """Отрисовка следующей фигуры"""
        painter = QPainter(self)
        next_piece, shape_index = self.game.get_next_piece()
        if not next_piece:
            return
        
        cell_size = 20
        offset_x = (self.width() - len(next_piece[0]) * cell_size) // 2
        offset_y = (self.height() - len(next_piece) * cell_size) // 2
        
        color = TetrisGame.COLORS[shape_index]
        
        for y, row in enumerate(next_piece):
            for x, cell in enumerate(row):
                if cell:
                    cell_x = offset_x + x * cell_size
                    cell_y = offset_y + y * cell_size
                    painter.fillRect(cell_x, cell_y, cell_size - 1, cell_size - 1, color)


class MainMenu(QWidget):
    """Главное меню"""
    
    play_clicked = pyqtSignal()
    rules_clicked = pyqtSignal()
    exit_clicked = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        """Инициализация UI"""
        self.setWindowTitle('Тетрис - Главное меню')
        self.setFixedSize(400, 500)
        
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(50, 50, 50, 50)
        
        # Заголовок
        title = QLabel('Главное меню')
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        layout.addStretch()
        
        # Кнопка "Играть"
        play_btn = QPushButton('Играть')
        play_btn.setMinimumHeight(60)
        play_btn.clicked.connect(self.play_clicked.emit)
        self.style_button(play_btn)
        layout.addWidget(play_btn)
        
        # Кнопка "Правила"
        rules_btn = QPushButton('Правила')
        rules_btn.setMinimumHeight(60)
        rules_btn.clicked.connect(self.rules_clicked.emit)
        self.style_button(rules_btn)
        layout.addWidget(rules_btn)
        
        # Кнопка "Выход"
        exit_btn = QPushButton('Выход')
        exit_btn.setMinimumHeight(60)
        exit_btn.clicked.connect(self.exit_clicked.emit)
        self.style_button(exit_btn)
        layout.addWidget(exit_btn)
        
        layout.addStretch()
        
        self.setLayout(layout)
        self.setStyleSheet("""
            QWidget {
                background-color: #1a1a1a;
            }
            QLabel {
                color: #ffffff;
            }
            QPushButton {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 2px solid #444444;
                border-radius: 5px;
                font-size: 18px;
            }
            QPushButton:hover {
                background-color: #3d3d3d;
                border-color: #555555;
            }
            QPushButton:pressed {
                background-color: #1d1d1d;
            }
        """)
    
    def style_button(self, button):
        """Стилизация кнопки"""
        pass  # Стили применяются через setStyleSheet


class RulesMenu(QWidget):
    """Меню правил"""
    
    back_clicked = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        """Инициализация UI"""
        self.setWindowTitle('Тетрис - Правила')
        self.setFixedSize(500, 600)
        
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Заголовок
        title = QLabel('Правила и управление')
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Правила
        rules_text = QLabel("""
        <h3>Цель игры:</h3>
        <p>Располагайте падающие фигуры так, чтобы заполнять горизонтальные линии. 
        Когда линия полностью заполнена, она исчезает, и вы получаете очки.</p>
        
        <h3>Управление:</h3>
        <p><b>←</b> - Движение влево<br>
        <b>→</b> - Движение вправо<br>
        <b>↓</b> - Ускоренное падение<br>
        <b>↑</b> или <b>Пробел</b> - Поворот фигуры<br>
        <b>Enter</b> - Мгновенное падение</p>
        
        <h3>Очки и уровни:</h3>
        <p>Очки начисляются за удаление линий. 
        Уровень повышается каждые 10 удаленных линий. 
        С повышением уровня скорость игры увеличивается.</p>
        
        <h3>Проигрыш:</h3>
        <p>Игра заканчивается, когда фигуры достигают верха игрового поля.</p>
        """)
        rules_text.setWordWrap(True)
        rules_text.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        layout.addWidget(rules_text)
        
        layout.addStretch()
        
        # Кнопка "Назад"
        back_btn = QPushButton('Главное меню')
        back_btn.setMinimumHeight(50)
        back_btn.clicked.connect(self.back_clicked.emit)
        layout.addWidget(back_btn)
        
        self.setLayout(layout)
        self.setStyleSheet("""
            QWidget {
                background-color: #1a1a1a;
            }
            QLabel {
                color: #ffffff;
                background-color: transparent;
            }
            QPushButton {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 2px solid #444444;
                border-radius: 5px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #3d3d3d;
                border-color: #555555;
            }
            QPushButton:pressed {
                background-color: #1d1d1d;
            }
        """)


class GameWindow(QWidget):
    """Окно игры"""
    
    game_over = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.game = TetrisGame()
        self.timer = QTimer()
        self.timer.timeout.connect(self.game_loop)
        self.init_ui()
        # Оверлей проигрыша (создаем поверх игрового окна)
        self.game_over_overlay = GameOverOverlay(self)
        self.game_over_overlay.hide()
        self.start_game()
    
    def init_ui(self):
        """Инициализация UI"""
        self.setWindowTitle('Тетрис')
        self.setFixedSize(600, 700)
        
        layout = QHBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Левая панель - информация
        info_panel = QVBoxLayout()
        info_panel.setSpacing(15)
        
        # Счет
        score_label = QLabel('Очки:')
        score_label.setFont(QFont('Arial', 14, QFont.Weight.Bold))
        info_panel.addWidget(score_label)
        
        self.score_value = QLabel('0')
        self.score_value.setFont(QFont('Arial', 18))
        info_panel.addWidget(self.score_value)
        
        # Уровень
        level_label = QLabel('Уровень:')
        level_label.setFont(QFont('Arial', 14, QFont.Weight.Bold))
        info_panel.addWidget(level_label)
        
        self.level_value = QLabel('0')
        self.level_value.setFont(QFont('Arial', 18))
        info_panel.addWidget(self.level_value)
        
        # Линии
        lines_label = QLabel('Линии:')
        lines_label.setFont(QFont('Arial', 14, QFont.Weight.Bold))
        info_panel.addWidget(lines_label)
        
        self.lines_value = QLabel('0')
        self.lines_value.setFont(QFont('Arial', 18))
        info_panel.addWidget(self.lines_value)
        
        info_panel.addStretch()
        
        # Следующая фигура
        next_label = QLabel('Следующая фигура:')
        next_label.setFont(QFont('Arial', 10, QFont.Weight.Bold))
        info_panel.addWidget(next_label)
        
        self.next_piece_widget = NextPieceWidget(self.game)
        self.next_piece_widget.setFixedSize(100, 100)
        self.next_piece_widget.setStyleSheet("background-color: #0a0a0a;")
        info_panel.addWidget(self.next_piece_widget)
        
        info_panel.addStretch()
        
        # Пауза
        pause_label = QLabel('Пауза: P')
        pause_label.setFont(QFont('Arial', 10))
        pause_label.setStyleSheet("color: #888888;")
        info_panel.addWidget(pause_label)
        
        info_widget = QWidget()
        info_widget.setLayout(info_panel)
        info_widget.setFixedWidth(150)
        layout.addWidget(info_widget)
        
        # Игровое поле
        self.game_board = GameBoardWidget(self.game)
        self.game_board.setFixedSize(300, 600)
        self.game_board.setStyleSheet("background-color: #0a0a0a; border: 2px solid #444444;")
        layout.addWidget(self.game_board)
        
        layout.addStretch()
        
        self.setLayout(layout)
        self.setStyleSheet("""
            QWidget {
                background-color: #1a1a1a;
            }
            QLabel {
                color: #ffffff;
                background-color: transparent;
            }
        """)
        
        self.paused = False
    
    def resizeEvent(self, event):
        """Растягиваем оверлей на все окно при изменении размера"""
        super().resizeEvent(event)
        if hasattr(self, "game_over_overlay") and self.game_over_overlay is not None:
            self.game_over_overlay.setGeometry(self.rect())
    
    def start_game(self):
        """Запуск игры"""
        self.game.reset()
        self.update_display()
        # Используем расчет скорости из класса игры
        speed = self.game.calculate_fall_speed()
        self.timer.start(speed)
    
    def game_loop(self):
        """Основной цикл игры"""
        if not self.paused and not self.game.game_over:
            self.game.drop_piece()
            self.update_display()
            
            # Обновление скорости согласно формуле из ТЗ
            # Δt = max(Tmin, Tбазовая - X × (Уровень - 1))
            speed = self.game.calculate_fall_speed()
            self.timer.setInterval(speed)
            
            if self.game.game_over:
                self.timer.stop()
                self.game_over.emit()
    
    def update_display(self):
        """Обновление отображения"""
        self.score_value.setText(str(self.game.score))
        # Отображаем уровень начиная с 1 для пользователя (внутри level начинается с 0)
        self.level_value.setText(str(self.game.level + 1))
        self.lines_value.setText(str(self.game.lines_cleared))
        self.game_board.update()
        self.next_piece_widget.update()
    
    
    def keyPressEvent(self, event: QKeyEvent):
        """Обработка нажатий клавиш"""
        if self.game.game_over:
            return
        
        if event.key() == Qt.Key.Key_Left:
            self.game.try_move(-1, 0)
        elif event.key() == Qt.Key.Key_Right:
            self.game.try_move(1, 0)
        elif event.key() == Qt.Key.Key_Down:
            self.game.try_move(0, 1, is_soft_drop=True)  # Soft drop: 1 очко за клетку
        elif event.key() == Qt.Key.Key_Up or event.key() == Qt.Key.Key_Space:
            self.game.try_rotate()
        elif event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            self.game.hard_drop()
        elif event.key() == Qt.Key.Key_P:
            self.paused = not self.paused
            if self.paused:
                self.timer.stop()
            else:
                # Используем расчет скорости из класса игры
                speed = self.game.calculate_fall_speed()
                self.timer.start(speed)
        
        self.update_display()


class GameOverOverlay(QWidget):
    """Оверлей проигрыша, который закрывает игровое поле"""
    
    main_menu_clicked = pyqtSignal()
    exit_clicked = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        # Полупрозрачный фон поверх игры
        self.setStyleSheet("background-color: rgba(0, 0, 0, 180);")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        layout.addStretch()
        
        # Центральная панель с информацией
        panel = QWidget(self)
        panel_layout = QVBoxLayout(panel)
        panel_layout.setSpacing(20)
        panel_layout.setContentsMargins(30, 30, 30, 30)
        
        title = QLabel("Конец игры", panel)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title.setFont(title_font)
        panel_layout.addWidget(title)
        
        # Подробная статистика отдельными лейблами (чтобы ничего не обрезалось)
        self.score_label = QLabel(panel)
        self.level_label = QLabel(panel)
        self.lines_label = QLabel(panel)
        for lbl in (self.score_label, self.level_label, self.lines_label):
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            panel_layout.addWidget(lbl)
        
        panel_layout.addStretch()
        
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)
        
        main_menu_btn = QPushButton("Главное меню", panel)
        main_menu_btn.setMinimumHeight(50)
        main_menu_btn.clicked.connect(self.main_menu_clicked.emit)
        buttons_layout.addWidget(main_menu_btn)
        
        exit_btn = QPushButton("Выход", panel)
        exit_btn.setMinimumHeight(50)
        exit_btn.clicked.connect(self.exit_clicked.emit)
        buttons_layout.addWidget(exit_btn)
        
        panel_layout.addLayout(buttons_layout)
        
        panel.setStyleSheet("""
            QWidget {
                background-color: #1a1a1a;
                border-radius: 8px;
            }
            QLabel {
                color: #ffffff;
                background-color: transparent;
            }
            QPushButton {
                background-color: #2d2d2d;
                color: #ffffff;
                border: 2px solid #444444;
                border-radius: 5px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #3d3d3d;
                border-color: #555555;
            }
            QPushButton:pressed {
                background-color: #1d1d1d;
            }
        """)
        
        # Обернем панель, чтобы она была по центру
        panel_container = QHBoxLayout()
        panel_container.addStretch()
        panel_container.addWidget(panel)
        panel_container.addStretch()
        
        layout.addLayout(panel_container)
        layout.addStretch()
    
    def set_stats(self, score: int, level: int, lines: int) -> None:
        """Обновление отображаемой статистики"""
        self.score_label.setText(f"Очки: <b>{score}</b>")
        self.level_label.setText(f"Уровень: <b>{level}</b>")
        self.lines_label.setText(f"Линии: <b>{lines}</b>")