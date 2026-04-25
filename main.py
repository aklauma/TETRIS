import sys

from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QApplication, QMainWindow, QStackedWidget

from tetris_game import TetrisGame
from ui import GameOverWidget, GameWidget, MainMenuWidget, RulesWidget


STYLE_SHEET = """
QMainWindow {
    background-color: #1a1a2e;
}
QWidget {
    background-color: #1a1a2e;
    color: #e0e0e0;
}
QPushButton {
    background-color: #16213e;
    color: #e0e0e0;
    border: 2px solid #0f3460;
    border-radius: 8px;
    padding: 12px 24px;
    font-size: 16px;
    font-weight: bold;
    min-width: 200px;
}
QPushButton:hover {
    background-color: #0f3460;
    border-color: #e94560;
}
QPushButton:pressed {
    background-color: #e94560;
}
QLabel {
    color: #e0e0e0;
}
"""


class TetrisWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Тетрис")
        self.setStyleSheet(STYLE_SHEET)

        self.game = TetrisGame()
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.menu_widget = MainMenuWidget(
            on_play=self._start_game,
            on_rules=self._show_rules,
            on_exit=self._exit_app,
        )
        self.stack.addWidget(self.menu_widget)

        self.rules_widget = RulesWidget(on_back=self._show_menu)
        self.stack.addWidget(self.rules_widget)

        self.game_widget = GameWidget(self.game, on_game_over=self._show_game_over)
        self.stack.addWidget(self.game_widget)

        self.game_over_widget = GameOverWidget(
            on_menu=self._show_menu,
            on_exit=self._exit_app,
        )
        self.stack.addWidget(self.game_over_widget)

        self.stack.setCurrentIndex(0)
        self.setMinimumSize(650, 760)
        self.resize(650, 760)

    def _start_game(self):
        self.stack.setCurrentIndex(2)
        self.game_widget.start_game()

    def _show_rules(self):
        self.stack.setCurrentIndex(1)

    def _show_menu(self):
        self.game_widget.timer.stop()
        self.stack.setCurrentIndex(0)

    def _show_game_over(self, score, level):
        self.game_over_widget.set_results(score, level)
        self.stack.setCurrentIndex(3)

    @staticmethod
    def _exit_app():
        QApplication.instance().quit()


def main():
    app = QApplication(sys.argv)
    app.setFont(QFont("Segoe UI", 12))
    window = TetrisWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
