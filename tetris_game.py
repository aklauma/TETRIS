import random

from PyQt6.QtGui import QColor


BOARD_WIDTH = 10
BOARD_HEIGHT = 20
CELL_SIZE = 32

PIECE_COLORS = {
    "I": QColor(0, 240, 240),
    "O": QColor(240, 240, 0),
    "T": QColor(160, 0, 240),
    "S": QColor(0, 240, 0),
    "Z": QColor(240, 0, 0),
    "J": QColor(0, 0, 240),
    "L": QColor(240, 160, 0),
}

SHAPES = {
    "I": [
        [(0, 1), (1, 1), (2, 1), (3, 1)],
        [(2, 0), (2, 1), (2, 2), (2, 3)],
        [(0, 2), (1, 2), (2, 2), (3, 2)],
        [(1, 0), (1, 1), (1, 2), (1, 3)],
    ],
    "O": [
        [(0, 0), (1, 0), (0, 1), (1, 1)],
        [(0, 0), (1, 0), (0, 1), (1, 1)],
        [(0, 0), (1, 0), (0, 1), (1, 1)],
        [(0, 0), (1, 0), (0, 1), (1, 1)],
    ],
    "T": [
        [(0, 1), (1, 1), (2, 1), (1, 0)],
        [(1, 0), (1, 1), (1, 2), (2, 1)],
        [(0, 1), (1, 1), (2, 1), (1, 2)],
        [(1, 0), (1, 1), (1, 2), (0, 1)],
    ],
    "S": [
        [(1, 0), (2, 0), (0, 1), (1, 1)],
        [(1, 0), (1, 1), (2, 1), (2, 2)],
        [(1, 1), (2, 1), (0, 2), (1, 2)],
        [(0, 0), (0, 1), (1, 1), (1, 2)],
    ],
    "Z": [
        [(0, 0), (1, 0), (1, 1), (2, 1)],
        [(2, 0), (1, 1), (2, 1), (1, 2)],
        [(0, 1), (1, 1), (1, 2), (2, 2)],
        [(1, 0), (0, 1), (1, 1), (0, 2)],
    ],
    "J": [
        [(0, 0), (0, 1), (1, 1), (2, 1)],
        [(1, 0), (2, 0), (1, 1), (1, 2)],
        [(0, 1), (1, 1), (2, 1), (2, 2)],
        [(1, 0), (1, 1), (0, 2), (1, 2)],
    ],
    "L": [
        [(2, 0), (0, 1), (1, 1), (2, 1)],
        [(1, 0), (1, 1), (1, 2), (2, 2)],
        [(0, 1), (1, 1), (2, 1), (0, 2)],
        [(0, 0), (1, 0), (1, 1), (1, 2)],
    ],
}

LINE_SCORES = {1: 40, 2: 100, 3: 300, 4: 1200}
T_BASE = 800
T_MIN = 100
X_COEFF = 50


class TetrisGame:
    """Игровая логика Тетриса."""

    def __init__(self):
        self.reset()

    def reset(self):
        self.board = [[None] * BOARD_WIDTH for _ in range(BOARD_HEIGHT)]
        self.score = 0
        self.level = 0
        self.lines_cleared = 0
        self.game_over = False
        self.current_piece = None
        self.next_piece = None
        self.piece_x = 0
        self.piece_y = 0
        self.rotation = 0
        self._spawn_piece()

    def _spawn_piece(self):
        if self.next_piece is None:
            self.next_piece = random.choice(list(SHAPES.keys()))
        self.current_piece = self.next_piece
        self.next_piece = random.choice(list(SHAPES.keys()))
        self.rotation = 0

        shape = SHAPES[self.current_piece][self.rotation]
        xs = [coord[0] for coord in shape]
        width = max(xs) - min(xs) + 1
        self.piece_x = (BOARD_WIDTH - width) // 2 - min(xs)
        self.piece_y = -min(coord[1] for coord in shape)

        if not self._is_valid_position(self.piece_x, self.piece_y, self.rotation):
            self.game_over = True

    def _is_valid_position(self, px, py, rot):
        shape = SHAPES[self.current_piece][rot]
        for dx, dy in shape:
            bx = px + dx
            by = py + dy
            if bx < 0 or bx >= BOARD_WIDTH:
                return False
            if by >= BOARD_HEIGHT:
                return False
            if by >= 0 and self.board[by][bx] is not None:
                return False
        return True

    def move_left(self):
        if self.current_piece and not self.game_over:
            if self._is_valid_position(self.piece_x - 1, self.piece_y, self.rotation):
                self.piece_x -= 1
                return True
        return False

    def move_right(self):
        if self.current_piece and not self.game_over:
            if self._is_valid_position(self.piece_x + 1, self.piece_y, self.rotation):
                self.piece_x += 1
                return True
        return False

    def rotate(self):
        if self.current_piece and not self.game_over:
            new_rot = (self.rotation + 1) % 4
            if self._is_valid_position(self.piece_x, self.piece_y, new_rot):
                self.rotation = new_rot
                return True
            for offset in [1, -1, 2, -2]:
                if self._is_valid_position(self.piece_x + offset, self.piece_y, new_rot):
                    self.piece_x += offset
                    self.rotation = new_rot
                    return True
        return False

    def soft_drop(self):
        if self.current_piece and not self.game_over:
            if self._is_valid_position(self.piece_x, self.piece_y + 1, self.rotation):
                self.piece_y += 1
                self.score += 1
                return True
            self._lock_piece()
        return False

    def hard_drop(self):
        if self.current_piece and not self.game_over:
            cells = 0
            while self._is_valid_position(self.piece_x, self.piece_y + 1, self.rotation):
                self.piece_y += 1
                cells += 1
            self.score += cells * 2
            self._lock_piece()

    def get_ghost_y(self):
        ghost_y = self.piece_y
        while self._is_valid_position(self.piece_x, ghost_y + 1, self.rotation):
            ghost_y += 1
        return ghost_y

    def tick(self):
        if self.current_piece and not self.game_over:
            if self._is_valid_position(self.piece_x, self.piece_y + 1, self.rotation):
                self.piece_y += 1
            else:
                self._lock_piece()

    def _lock_piece(self):
        shape = SHAPES[self.current_piece][self.rotation]
        color = PIECE_COLORS[self.current_piece]
        for dx, dy in shape:
            bx = self.piece_x + dx
            by = self.piece_y + dy
            if 0 <= bx < BOARD_WIDTH and 0 <= by < BOARD_HEIGHT:
                self.board[by][bx] = color
        self._clear_lines()
        self._spawn_piece()

    def _clear_lines(self):
        lines_to_remove = []
        for y in range(BOARD_HEIGHT):
            if all(cell is not None for cell in self.board[y]):
                lines_to_remove.append(y)

        if lines_to_remove:
            cleared = len(lines_to_remove)
            self.score += LINE_SCORES.get(cleared, 1200) * (self.level + 1)
            self.lines_cleared += cleared
            self.level = self.lines_cleared // 10

            for y in sorted(lines_to_remove, reverse=True):
                del self.board[y]
            for _ in range(cleared):
                self.board.insert(0, [None] * BOARD_WIDTH)

    def get_fall_interval(self):
        return max(T_MIN, T_BASE - X_COEFF * self.level)
