from PyQt6.QtWidgets import QMainWindow, QStackedWidget, QMessageBox, QApplication
from PyQt6.QtCore import Qt, QTimer

from ui.search_page import SearchPage
from ui.player_card_page import PlayerCardPage
from ui.glass_container import GlassContainer
from ui.title_bar import TitleBar
from ui.loading_overlay import LoadingOverlay
from ui.settings_overlay import SettingsOverlay

from services.api_client import ApiClient
from services.api_checker import ApiChecker
from services.hotkey_manager import HotkeyManager


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )

        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.resize(950, 700)

        self.container = GlassContainer(self)

        self.title_bar = TitleBar(self)
        self.stack = QStackedWidget()

        self.search_page = SearchPage()
        self.player_page = PlayerCardPage()

        self.stack.addWidget(self.search_page)
        self.stack.addWidget(self.player_page)

        self.container.layout.addWidget(self.title_bar)
        self.container.layout.addWidget(self.stack)

        self.setCentralWidget(self.container)
        self.loading_overlay = LoadingOverlay(self)
        
        self.loading_overlay.hide()
        self.hotkey_manager = HotkeyManager(self)
        
        self.settings_overlay = SettingsOverlay(self, self.hotkey_manager)
        backend_url = "http://localhost:8001"
        
        self.api = ApiClient(backend_url)
        self.api_checker = ApiChecker(backend_url)
        
        self.search_page.searchRequested.connect(self.search_player)
        self.search_page.checkApiRequested.connect(self.check_api_stats)
        
        self.search_page.settingsRequested.connect(self.show_settings)
        self.api.playerLoaded.connect(self.on_player_loaded)
        
        self.api.errorOccurred.connect(self.show_error)
        self.api_checker.resultReady.connect(self.on_api_check_result)
        
        self.player_page.closeRequested.connect(self.close)
        self.player_page.refreshRequested.connect(self.refresh)
        
        self.player_page.backToSearchRequested.connect(self.back_to_search)
        self.settings_overlay.closed.connect(self.on_settings_closed)

        self.hotkey_manager.toggled.connect(self.toggle_visibility)
        QTimer.singleShot(0, lambda: self.hotkey_manager.attach_to_window(self))

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, 'loading_overlay'):
            x = (self.width() - self.loading_overlay.width()) // 2
            y = (self.height() - self.loading_overlay.height()) // 2
            self.loading_overlay.move(x, y)

    def toggle_visibility(self):
        """Глобальное переключение видимости окна"""
        if self.isVisible():
            self.hide()
        else:
            self.show()
            self.raise_()
            self.activateWindow()
        
        if hasattr(self, 'settings_overlay') and self.settings_overlay.isVisible():
            self.settings_overlay.update_status_label()

    def search_player(self, nickname):
        """Поиск игрока по Steam ID"""
        if self.stack.currentWidget() == self.player_page:
            self.search_page.input.clear()
        
        self.loading_overlay.show_with_animation()
        x = (self.width() - self.loading_overlay.width()) // 2
        y = (self.height() - self.loading_overlay.height()) // 2
        self.loading_overlay.move(x, y)
        self.api.fetch_player(nickname)

    def check_api_stats(self):
        """Проверка API бэкенда"""
        self.loading_overlay.show_with_animation()
        self.api_checker.check_api_status()

    def on_api_check_result(self, result):
        """Обработка результата проверки API"""
        self.loading_overlay.hide_with_animation()
        
        msg = QMessageBox(self)
        msg.setWindowTitle("Backend Status")
        msg.setText(result["message"])
        msg.setDetailedText(result.get("details", ""))
        msg.setStyleSheet("""
            QMessageBox {
                background: #12141A;
                color: #E8EAF0;
            }
            QMessageBox QLabel {
                color: #E8EAF0;
            }
            QPushButton {
                background: #4F8CFF;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
                min-width: 80px;
            }
            QPushButton:hover {
                background: #6EA8FF;
            }
        """)
        msg.exec()

    def show_settings(self):
        """Показать окно настроек"""
        self.settings_overlay.show_settings()
    
    def on_settings_closed(self):
        pass

    def on_player_loaded(self, data):
        """Обработка загрузки данных игрока"""
        self.loading_overlay.hide_with_animation()
        self.player_page.set_player_data(data)
        self.stack.setCurrentWidget(self.player_page)

    def refresh(self):
        if hasattr(self.player_page, 'current_steam_id') and self.player_page.current_steam_id:
            self.search_player(str(self.player_page.current_steam_id))
    
    def back_to_search(self):
        self.stack.setCurrentWidget(self.search_page)
        self.search_page.input.clear()
        self.search_page.input.setFocus()

    def show_error(self, error_message):
        self.loading_overlay.hide_with_animation()
        QMessageBox.critical(self, "Error", f"Failed to load player data:\n{error_message}")
        self.back_to_search()

    def closeEvent(self, event):
        reply = QMessageBox.question(
            self, 
            'Exit', 
            'Are you sure you want to exit?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            if hasattr(self, 'hotkey_manager'):
                self.hotkey_manager.unregister()
            if hasattr(self, 'settings_overlay'):
                self.settings_overlay.close()
            event.accept()
            QApplication.quit()
        else:
            event.ignore()