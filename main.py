import sys
from PyQt6.QtWidgets import QApplication, QStackedWidget
from PyQt6.QtCore import Qt
from ui import MainMenu, RulesMenu, GameWindow

class TetrisApp(QStackedWidget):
    "Главное приложение"
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        "Инициализация UI"
        # Главное меню
        self.main_menu = MainMenu()
        self.main_menu.play_clicked.connect(self.show_game)
        self.main_menu.rules_clicked.connect(self.show_rules)
        self.main_menu.exit_clicked.connect(self.close_app)
        self.addWidget(self.main_menu)
        
        # Меню правил
        self.rules_menu = RulesMenu()
        self.rules_menu.back_clicked.connect(self.show_main_menu)
        self.addWidget(self.rules_menu)
        
        # Окно игры
        self.game_window = GameWindow()
        self.game_window.game_over.connect(self.show_game_over)
        self.addWidget(self.game_window)
        
        # Показываем главное меню
        self.setCurrentWidget(self.main_menu)
        self.setWindowTitle('Тетрис')
        self.setFixedSize(400, 500)
    
    def show_main_menu(self):
        """Показать главное меню"""
        self.setCurrentWidget(self.main_menu)
        self.setFixedSize(400, 500)
    
    def show_rules(self):
        """Показать меню правил"""
        self.setCurrentWidget(self.rules_menu)
        self.setFixedSize(500, 600)
    
    def show_game(self):
        """Показать игру"""
        self.setCurrentWidget(self.game_window)
        self.setFixedSize(600, 700)
        self.game_window.start_game()
    
    def show_game_over(self):
        """Показать оверлей проигрыша поверх игрового окна"""
        game = self.game_window.game
        # Настраиваем оверлей внутри окна игры
        overlay = self.game_window.game_over_overlay
        overlay.setGeometry(self.game_window.rect())
        overlay.set_stats(game.score, game.level + 1, game.lines_cleared)
        # Обновляем сигналы (на случай повторной игры)
        try:
            overlay.main_menu_clicked.disconnect()
        except TypeError:
            # Не было подключений — игнорируем
            pass
        try:
            overlay.exit_clicked.disconnect()
        except TypeError:
            pass
        overlay.main_menu_clicked.connect(self.on_main_menu_from_game_over)
        overlay.exit_clicked.connect(self.close_app)
        overlay.show()
        overlay.raise_()
    
    def on_main_menu_from_game_over(self):
        """Переход в главное меню из диалога проигрыша"""
        self.show_main_menu()
    
    def close_app(self):
        """Закрытие приложения"""
        self.close()
    
    def closeEvent(self, event):
        """Обработка закрытия окна (крестик, Alt+F4)"""
        # Останавливаем таймер игры, если он запущен
        if hasattr(self.game_window, 'timer'):
            self.game_window.timer.stop()
        event.accept()


def main():
    """Точка входа"""
    app = QApplication(sys.argv)
    
    # Установка стиля приложения
    app.setStyle('Fusion')
    
    window = TetrisApp()
    window.show()
    
    sys.exit(app.exec())


if __name__ == '__main__':
    main()