import sys

from PyQt6 import uic

from PyQt6.QtCore import Qt, QTimer

from PyQt6.QtGui import QFont

from PyQt6.QtWidgets import (

    QApplication,

    QMainWindow,

    QPushButton,

    QSizePolicy,

    QStackedWidget,

    QVBoxLayout,

    QWidget,

)



from game_widgets import BoardWidget, NextPieceWidget

from tetris_game import TetrisGame

from theme import STYLE_SHEET, apply_transparent_text

from paths import UI_DIR, load_bundled_font
from ui_scale import BASE_HEIGHT, BASE_WIDTH, wrap_scalable

MIN_WINDOW_WIDTH = BASE_WIDTH

MIN_WINDOW_HEIGHT = BASE_HEIGHT





def _load_ui_content(ui_name: str) -> QWidget:

    """Загружает .ui с фиксированной вёрсткой 800x600."""

    content = QWidget()

    content.resize(BASE_WIDTH, BASE_HEIGHT)

    uic.loadUi(str(UI_DIR / ui_name), content)

    apply_transparent_text(content)

    return content





def _load_main_menu_content() -> QWidget:

    form = uic.loadUi(str(UI_DIR / "main_menu.ui"))

    content = form.takeCentralWidget()

    content.resize(BASE_WIDTH, BASE_HEIGHT)

    form.deleteLater()

    apply_transparent_text(content)

    return content





def _embed_scalable(screen: QWidget, content: QWidget) -> QWidget:

    viewport = wrap_scalable(content)

    layout = QVBoxLayout(screen)

    layout.setContentsMargins(0, 0, 0, 0)

    layout.addWidget(viewport)

    return content





class MenuScreen(QWidget):

    def __init__(self, on_play, on_rules, on_exit, parent=None):

        super().__init__(parent)

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)



        content = _load_main_menu_content()

        _embed_scalable(self, content)



        content.findChild(QPushButton, "btn_play").clicked.connect(on_play)

        content.findChild(QPushButton, "btn_rules").clicked.connect(on_rules)

        content.findChild(QPushButton, "btn_exit").clicked.connect(on_exit)





class RulesScreen(QWidget):

    def __init__(self, on_back, parent=None):

        super().__init__(parent)

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)



        content = _load_ui_content("rules_control.ui")

        _embed_scalable(self, content)

        content.findChild(QPushButton, "btn_main_menu").clicked.connect(on_back)





class GameScreen(QWidget):

    CONTROLS_HINT = (

        "<html><head/><body>"

        "<p>← → - движение   ↑ - поворот</p>"

        "<p>↓ - soft drop   Пробел - hard drop</p>"

        "<p>P - пауза</p>"

        "</body></html>"

    )



    def __init__(self, game: TetrisGame, on_game_over, on_menu, parent=None):

        super().__init__(parent)

        self.game = game

        self.on_game_over = on_game_over

        self.on_menu = on_menu

        self.paused = False

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)



        self.ui = _load_ui_content("game_screen.ui")



        field_layout = QVBoxLayout(self.ui.widget_game_field)

        field_layout.setContentsMargins(0, 0, 0, 0)

        self.board_widget = BoardWidget(game, self.ui.widget_game_field)

        field_layout.addWidget(self.board_widget)



        next_layout = QVBoxLayout(self.ui.widget_next_figure)

        next_layout.setContentsMargins(0, 0, 0, 0)

        self.next_piece_widget = NextPieceWidget(game, self.ui.widget_next_figure)

        next_layout.addWidget(self.next_piece_widget)



        self._viewport = wrap_scalable(self.ui)
        self._viewport.refresh_snapshots()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._viewport)

        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._tick)

    def showEvent(self, event):
        super().showEvent(event)
        QTimer.singleShot(0, self._refresh_layout)

    def _refresh_layout(self):
        self._viewport.relayout()
        self.board_widget.updateGeometry()
        self.next_piece_widget.updateGeometry()
        self.board_widget.update()
        self.next_piece_widget.update()

    def start_game(self):
        self.game.reset()
        self.paused = False
        self.ui.label_controls_hint.setText(self.CONTROLS_HINT)
        self._update_display()
        self.timer.start(self.game.get_fall_interval())
        self.setFocus()
        QTimer.singleShot(0, self._refresh_layout)



    def stop_timer(self):

        self.timer.stop()



    def _tick(self):

        if not self.paused and not self.game.game_over:

            self.game.tick()

            self._update_display()

            if self.game.game_over:

                self.timer.stop()

                self.on_game_over(self.game.score, self.game.level)



    def _update_display(self):

        self.ui.label_score_value.setText(str(self.game.score))

        self.ui.label_level_value.setText(str(self.game.level))

        self.board_widget.update()

        self.next_piece_widget.update()

        interval = self.game.get_fall_interval()

        if self.timer.interval() != interval:

            self.timer.setInterval(interval)



    def keyPressEvent(self, event):

        key = event.key()

        text = event.text().lower()



        if key == Qt.Key.Key_Escape:

            self.on_menu()

            return



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

        elif key in (Qt.Key.Key_Down, Qt.Key.Key_S) or text == "ы":

            self.game.soft_drop()

        elif key == Qt.Key.Key_Space:

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

            self.ui.label_controls_hint.setText(

                '<html><head/><body><p align="center">'

                '<span style=" font-size:14pt; font-weight:600; color:#e94560;">'

                "ПАУЗА</span></p></body></html>"

            )

        else:

            self.ui.label_controls_hint.setText(self.CONTROLS_HINT)

            self.timer.start(self.game.get_fall_interval())





class GameOverScreen(QWidget):

    def __init__(self, on_menu, on_exit, parent=None):

        super().__init__(parent)

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)



        self.ui = _load_ui_content("game_over.ui")

        _embed_scalable(self, self.ui)



        self.ui.btn_main_menu.clicked.connect(on_menu)

        self.ui.btn_exit.clicked.connect(on_exit)



    def set_results(self, score: int, level: int):

        self.ui.label_final_score_value.setText(str(score))

        self.ui.label_final_level_value.setText(str(level))





class TetrisWindow(QMainWindow):

    INDEX_MENU = 0

    INDEX_RULES = 1

    INDEX_GAME = 2

    INDEX_GAME_OVER = 3



    def __init__(self):

        super().__init__()

        self.setWindowTitle("Тетрис")

        self.setStyleSheet(STYLE_SHEET)



        self.game = TetrisGame()

        self.stack = QStackedWidget()

        self.setCentralWidget(self.stack)



        self.menu_screen = MenuScreen(

            on_play=self._start_game,

            on_rules=self._show_rules,

            on_exit=self._exit_app,

        )

        self.stack.addWidget(self.menu_screen)



        self.rules_screen = RulesScreen(on_back=self._show_menu)

        self.stack.addWidget(self.rules_screen)



        self.game_screen = GameScreen(

            self.game,

            on_game_over=self._show_game_over,

            on_menu=self._show_menu,

        )

        self.stack.addWidget(self.game_screen)



        self.game_over_screen = GameOverScreen(

            on_menu=self._show_menu,

            on_exit=self._exit_app,

        )

        self.stack.addWidget(self.game_over_screen)



        self.stack.setCurrentIndex(self.INDEX_MENU)

        self.setMinimumSize(MIN_WINDOW_WIDTH, MIN_WINDOW_HEIGHT)

        self.resize(MIN_WINDOW_WIDTH, MIN_WINDOW_HEIGHT)



    def _start_game(self):

        self.stack.setCurrentIndex(self.INDEX_GAME)

        self.game_screen.start_game()



    def _show_rules(self):

        self.stack.setCurrentIndex(self.INDEX_RULES)



    def _show_menu(self):

        self.game_screen.stop_timer()

        self.stack.setCurrentIndex(self.INDEX_MENU)



    def _show_game_over(self, score: int, level: int):

        self.game_over_screen.set_results(score, level)

        self.stack.setCurrentIndex(self.INDEX_GAME_OVER)



    @staticmethod

    def _exit_app():

        QApplication.instance().quit()





def main():
    app = QApplication(sys.argv)
    font_family = load_bundled_font() or "Segoe UI"
    app.setFont(QFont(font_family, 12))

    window = TetrisWindow()

    window.show()

    sys.exit(app.exec())





if __name__ == "__main__":

    main()

