from PyQt6.QtCore import QRect
from PyQt6.QtGui import QColor, QPainter, QPen
from PyQt6.QtWidgets import QSizePolicy, QWidget

from tetris_game import BOARD_HEIGHT, BOARD_WIDTH, PIECE_COLORS, SHAPES

try:
    from theme import COLORS
except ImportError:
    COLORS = {"board": "#0a0a1e"}

BOARD_BG = QColor(COLORS.get("board", "#0a0a1e"))


class BoardWidget(QWidget):
    def __init__(self, game, parent=None):
        super().__init__(parent)
        self.game = game
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)
        painter.fillRect(self.rect(), BOARD_BG)

        cell_size = max(
            8,
            min((self.width() - 1) // BOARD_WIDTH, (self.height() - 1) // BOARD_HEIGHT),
        )
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
                    self._draw_cell(
                        painter, x, y, self.game.board[y][x], cell_size, offset_x, offset_y
                    )

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
                        painter,
                        bx,
                        by,
                        ghost_color,
                        cell_size,
                        offset_x,
                        offset_y,
                        is_ghost=True,
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
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), BOARD_BG)
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
