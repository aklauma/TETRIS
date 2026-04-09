from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QColor
import random

class TetrisGame:
    """Класс для логики игры Тетрис"""
    
    BOARD_WIDTH = 10
    BOARD_HEIGHT = 20
    
    # Параметры для расчета скорости падения фигур
    # Формула: Δt = max(Tmin, Tбазовая - X × (Уровень - 1))
    T_MIN = 50  # Минимальный интервал (предел скорости, при котором игра управляема)
    T_BASE = 500  # Базовый интервал (скорость на первом уровне)
    X_COEFFICIENT = 50  # Коэффициент ускорения на уровень
    
    # Фигуры Тетриса (тетромино)
    SHAPES = [
        [[1, 1, 1, 1]],  # I
        [[1, 1], [1, 1]],  # O
        [[0, 1, 0], [1, 1, 1]],  # T
        [[0, 1, 1], [1, 1, 0]],  # S
        [[1, 1, 0], [0, 1, 1]],  # Z
        [[1, 0, 0], [1, 1, 1]],  # J
        [[0, 0, 1], [1, 1, 1]],  # L
    ]
    
    COLORS = [
        QColor(0, 255, 255),  # Cyan для I
        QColor(255, 255, 0),  # Yellow для O
        QColor(128, 0, 128),  # Purple для T
        QColor(0, 255, 0),    # Green для S
        QColor(255, 0, 0),    # Red для Z
        QColor(0, 0, 255),    # Blue для J
        QColor(255, 165, 0),  # Orange для L
    ]
    
    def __init__(self):
        self.reset()
    
    def reset(self):
        """Сброс игры"""
        self.board = [[0 for _ in range(self.BOARD_WIDTH)] 
                     for _ in range(self.BOARD_HEIGHT)]
        self.current_piece = None
        self.next_piece = None
        self.current_x = 0
        self.current_y = 0
        self.current_shape_index = 0
        self.next_shape_index = 0
        self.score = 0
        self.level = 0  # Уровень начинается с 0 (N в формуле)
        self.lines_cleared = 0
        self.game_over = False
        self.spawn_new_piece()
        self.spawn_new_piece()  # Создаем текущую и следующую фигуру
    
    def spawn_new_piece(self):
        """Создание новой фигуры"""
        if self.next_piece is None:
            # Первый вызов - создаем обе фигуры
            self.current_shape_index = random.randint(0, len(self.SHAPES) - 1)
            self.next_shape_index = random.randint(0, len(self.SHAPES) - 1)
        else:
            # Последующие вызовы - используем следующую фигуру
            self.current_shape_index = self.next_shape_index
            self.next_shape_index = random.randint(0, len(self.SHAPES) - 1)
        
        self.current_piece = self.SHAPES[self.current_shape_index]
        self.next_piece = self.SHAPES[self.next_shape_index]
        self.current_x = self.BOARD_WIDTH // 2 - len(self.current_piece[0]) // 2
        self.current_y = 0
        
        # Проверка на проигрыш: фигура должна полностью помещаться в начальной позиции
        if not self.can_spawn_piece(self.current_piece, self.current_x, self.current_y):
            self.game_over = True
    
    def get_next_piece(self):
        """Получить следующую фигуру"""
        return self.next_piece, self.next_shape_index
    
    def rotate_piece(self, piece):
        """Поворот фигуры на 90 градусов"""
        return [[piece[y][x] for y in range(len(piece)-1, -1, -1)] 
                for x in range(len(piece[0]))]
    
    def check_collision(self, piece, x, y):
        """Проверка столкновения"""
        for py, row in enumerate(piece):
            for px, cell in enumerate(row):
                if cell:
                    nx, ny = x + px, y + py
                    # Проверка выхода за границы доски
                    if nx < 0 or nx >= self.BOARD_WIDTH:
                        return True
                    # Проверка выхода за нижнюю границу
                    if ny >= self.BOARD_HEIGHT:
                        return True
                    # Проверка столкновения с блоками на доске (только если блок в пределах доски)
                    if ny >= 0 and ny < self.BOARD_HEIGHT and self.board[ny][nx]:
                        return True
        return False
    
    def can_spawn_piece(self, piece, x, y):
        """
        Проверка возможности появления фигуры в начальной позиции
        Фигура должна полностью помещаться в пределах доски
        """
        for py, row in enumerate(piece):
            for px, cell in enumerate(row):
                if cell:
                    nx, ny = x + px, y + py
                    # Проверка выхода за границы доски по горизонтали
                    if nx < 0 or nx >= self.BOARD_WIDTH:
                        return False
                    # Проверка выхода за верхнюю границу (ny < 0)
                    if ny < 0:
                        return False
                    # Проверка выхода за нижнюю границу
                    if ny >= self.BOARD_HEIGHT:
                        return False
                    # Проверка столкновения с блоками на доске
                    if self.board[ny][nx]:
                        return False
        return True
    
    def try_move(self, dx, dy, is_soft_drop=False):
        """Попытка переместить фигуру"""
        if self.game_over:
            return False
        
        new_x = self.current_x + dx
        new_y = self.current_y + dy
        
        if not self.check_collision(self.current_piece, new_x, new_y):
            self.current_x = new_x
            self.current_y = new_y
            # Подсчет очков за soft drop (1 очко за клетку)
            if is_soft_drop and dy > 0:
                self.score += 1
            return True
        return False
    
    def try_rotate(self):
        """Попытка повернуть фигуру"""
        if self.game_over:
            return False
        
        rotated = self.rotate_piece(self.current_piece)
        if not self.check_collision(rotated, self.current_x, self.current_y):
            self.current_piece = rotated
            return True
        return False
    
    def drop_piece(self):
        """Опустить фигуру вниз (автоматическое падение)"""
        if self.game_over:
            return False
        
        if not self.try_move(0, 1):
            # Фигура достигла дна или столкнулась
            self.place_piece()
            self.clear_lines()
            self.spawn_new_piece()
            return False
        return True
    
    def hard_drop(self):
        """Мгновенное падение фигуры (2 очка за клетку)"""
        if self.game_over:
            return
        
        cells_dropped = 0
        while self.try_move(0, 1):
            cells_dropped += 1
        
        # Подсчет очков за hard drop (2 очка за клетку)
        self.score += cells_dropped * 2
        
        self.place_piece()
        self.clear_lines()
        self.spawn_new_piece()
    
    def place_piece(self):
        """Размещение фигуры на доске"""
        for py, row in enumerate(self.current_piece):
            for px, cell in enumerate(row):
                if cell:
                    ny = self.current_y + py
                    nx = self.current_x + px
                    if ny >= 0:
                        self.board[ny][nx] = self.current_shape_index + 1
    
    def clear_lines(self):
        """Очистка заполненных линий"""
        lines_to_clear = []
        for y in range(self.BOARD_HEIGHT):
            if all(self.board[y]):
                lines_to_clear.append(y)
        
        for y in lines_to_clear:
            del self.board[y]
            self.board.insert(0, [0 for _ in range(self.BOARD_WIDTH)])
        
        cleared = len(lines_to_clear)
        if cleared > 0:
            self.lines_cleared += cleared
            
            # Подсчет очков согласно таблице из ТЗ
            # N - текущий уровень (начинается с 0)
            N = self.level
            if cleared == 1:
                # Одиночная линия: 40*(N + 1)
                self.score += 40 * (N + 1)
            elif cleared == 2:
                # Двойная линия: 100*(N + 1)
                self.score += 100 * (N + 1)
            elif cleared == 3:
                # Тройная линия: 300*(N + 1)
                self.score += 300 * (N + 1)
            elif cleared >= 4:
                # Тетрис (4 линии): 1200*(N + 1)
                self.score += 1200 * (N + 1)
            
            # Повышение уровня каждые 10 линий
            self.level = self.lines_cleared // 10
    
    def calculate_fall_speed(self):
        """
        Расчет скорости падения фигур согласно ТЗ
        Формула: Δt = max(Tmin, Tбазовая - X × (Уровень - 1))
        
        Возвращает интервал времени в миллисекундах
        """
        # Уровень в коде начинается с 0, но для формулы используем (level + 1) как отображаемый уровень
        # Для уровня 0 (отображается как 1): (1 - 1) = 0, используется Tбазовая
        display_level = self.level + 1
        delta_t = max(
            self.T_MIN,
            self.T_BASE - self.X_COEFFICIENT * (display_level - 1)
        )
        return int(delta_t)
    
    def get_board(self):
        """Получить текущее состояние доски"""
        board = [row[:] for row in self.board]
        
        # Добавить текущую фигуру
        if self.current_piece and not self.game_over:
            for py, row in enumerate(self.current_piece):
                for px, cell in enumerate(row):
                    if cell:
                        ny = self.current_y + py
                        nx = self.current_x + px
                        if 0 <= ny < self.BOARD_HEIGHT and 0 <= nx < self.BOARD_WIDTH:
                            board[ny][nx] = self.current_shape_index + 1
        
        return board