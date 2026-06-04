from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QHBoxLayout, QPushButton
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QMetaObject, Q_ARG, pyqtSlot
from PyQt6.QtGui import QKeyEvent

from styles.theme import Theme
from ui.animated_button import AnimatedButton
import keyboard


class SettingsOverlay(QWidget):
    closed = pyqtSignal()
    hotkeyChanged = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.setVisible(False)
        self.setFixedSize(500, 420)
        
        # Основной контейнер
        self.container = QWidget(self)
        self.container.setObjectName("Glass")
        self.container.setGeometry(0, 0, self.width(), self.height())
        self.container.setStyleSheet("""
            #Glass {
                background: rgba(18, 20, 25, 250);
                border: 1px solid rgba(255,255,255,12);
                border-radius: 20px;
            }
        """)
        
        layout = QVBoxLayout(self.container)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Title
        title = QLabel("⚙ SETTINGS")
        title.setStyleSheet(f"color: {Theme.ACCENT}; font-size: 18px; font-weight: bold; letter-spacing: 2px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Hotkey section
        hotkey_label = QLabel("GLOBAL HOTKEY")
        hotkey_label.setStyleSheet(f"color: {Theme.TEXT}; font-size: 13px; font-weight: bold; margin-top: 10px;")
        
        hotkey_desc = QLabel("Press any key combination to set as hotkey for showing/hiding the overlay\n(Works even when app is minimized or not in focus)")
        hotkey_desc.setStyleSheet(f"color: {Theme.MUTED}; font-size: 11px;")
        hotkey_desc.setWordWrap(True)
        
        # Поле для ввода хоткея
        self.hotkey_input = QLineEdit()
        self.hotkey_input.setPlaceholderText("Click here and press any key...")
        self.hotkey_input.setReadOnly(True)
        self.hotkey_input.setMinimumHeight(50)
        self.hotkey_input.setStyleSheet(f"""
            QLineEdit {{
                background: {Theme.CARD};
                border: 2px solid {Theme.ACCENT};
                border-radius: 12px;
                padding: 15px;
                color: {Theme.TEXT};
                font-size: 16px;
                text-align: center;
                font-weight: bold;
            }}
        """)
        self.hotkey_input.mousePressEvent = self.on_input_click
        
        self.current_hotkey = "`"
        self.hotkey_input.setText(f"Current: {self.current_hotkey}")
        
        # Кнопка сброса
        reset_btn = QPushButton("Reset to Default (`)")
        reset_btn.setMinimumHeight(40)
        reset_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {Theme.ACCENT};
                border: 1px solid {Theme.ACCENT};
                border-radius: 10px;
                padding: 10px;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background: rgba(79, 140, 255, 30);
            }}
        """)
        reset_btn.clicked.connect(self.reset_hotkey)
        
        hotkey_layout = QHBoxLayout()
        hotkey_layout.addWidget(self.hotkey_input, stretch=3)
        hotkey_layout.addWidget(reset_btn, stretch=1)
        
        # Статус видимости
        self.status_label = QLabel("● OVERLAY VISIBLE")
        self.status_label.setStyleSheet(f"color: {Theme.SUCCESS}; font-size: 13px; font-weight: bold;")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Текущий активный хоткей
        self.active_hotkey_label = QLabel(f"Active hotkey: {self.current_hotkey}")
        self.active_hotkey_label.setStyleSheet(f"color: {Theme.MUTED}; font-size: 12px;")
        self.active_hotkey_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Кнопки управления
        buttons_layout = QHBoxLayout()
        self.toggle_btn = AnimatedButton("HIDE OVERLAY", "secondary")
        self.toggle_btn.clicked.connect(self.toggle_overlay_visibility)
        
        self.close_btn = AnimatedButton("CLOSE SETTINGS", "primary")
        self.close_btn.clicked.connect(self.hide_settings)
        
        buttons_layout.addWidget(self.toggle_btn)
        buttons_layout.addWidget(self.close_btn)
        
        layout.addWidget(title)
        layout.addSpacing(10)
        layout.addWidget(hotkey_label)
        layout.addWidget(hotkey_desc)
        layout.addSpacing(10)
        layout.addLayout(hotkey_layout)
        layout.addSpacing(10)
        layout.addWidget(self.active_hotkey_label)
        layout.addSpacing(20)
        layout.addWidget(self.status_label)
        layout.addStretch()
        layout.addLayout(buttons_layout)
        
        self.parent_window = parent
        self.is_listening = False
        self.current_hotkey_handler = None
        self.hotkey_thread_timer = None
        
        # Регистрируем начальный хоткей
        self.register_hotkey(self.current_hotkey)
    
    def on_input_click(self, event):
        """Клик по полю ввода - начинаем прослушивание"""
        self.start_listening()
    
    def start_listening(self):
        """Начинаем глобальное прослушивание клавиши"""
        if self.is_listening:
            return
            
        self.is_listening = True
        self.hotkey_input.clear()
        self.hotkey_input.setPlaceholderText("Press any key combination...")
        self.hotkey_input.setStyleSheet(f"""
            QLineEdit {{
                background: {Theme.ACCENT};
                border: 2px solid {Theme.ACCENT};
                border-radius: 12px;
                padding: 15px;
                color: {Theme.TEXT};
                font-size: 16px;
                text-align: center;
                font-weight: bold;
            }}
        """)
        
        # Используем QTimer для автоматической остановки
        self.hotkey_thread_timer = QTimer()
        self.hotkey_thread_timer.setSingleShot(True)
        self.hotkey_thread_timer.timeout.connect(self.stop_listening)
        self.hotkey_thread_timer.start(5000)
        
        # Хук на клавиши
        keyboard.hook(self.on_key_press_callback, suppress=False)
    
    def on_key_press_callback(self, event):
        """Обработка нажатия клавиши - вызывается из потока keyboard"""
        if not self.is_listening:
            return
        
        if event.event_type == keyboard.KEY_DOWN:
            # Используем QTimer для безопасного вызова из другого потока
            QTimer.singleShot(0, lambda: self.process_hotkey(event.name))
    
    @pyqtSlot(str)
    def process_hotkey(self, key_name):
        """Безопасная обработка хоткея в главном потоке"""
        if not self.is_listening:
            return
        
        # Игнорируем модификаторы если они одни
        if key_name in ['ctrl', 'alt', 'shift', 'cmd', 'windows']:
            return
        
        # Формируем хоткей
        hotkey_parts = []
        
        # Проверяем зажатые модификаторы
        if keyboard.is_pressed('ctrl'):
            hotkey_parts.append('ctrl')
        if keyboard.is_pressed('alt'):
            hotkey_parts.append('alt')
        if keyboard.is_pressed('shift'):
            hotkey_parts.append('shift')
        
        # Нормализуем имя клавиши
        if key_name == 'space':
            key_name = 'space'
        elif key_name == 'enter':
            key_name = 'enter'
        elif len(key_name) == 1:
            key_name = key_name.lower()
        
        hotkey_parts.append(key_name)
        new_hotkey = '+'.join(hotkey_parts)
        
        # Обновляем хоткей
        self.update_hotkey(new_hotkey)
        self.stop_listening()
    
    def stop_listening(self):
        """Останавливаем прослушивание"""
        self.is_listening = False
        
        if self.hotkey_thread_timer:
            self.hotkey_thread_timer.stop()
            self.hotkey_thread_timer = None
        
        try:
            keyboard.unhook_all()
        except:
            pass
        
        self.hotkey_input.setStyleSheet(f"""
            QLineEdit {{
                background: {Theme.CARD};
                border: 2px solid {Theme.ACCENT};
                border-radius: 12px;
                padding: 15px;
                color: {Theme.TEXT};
                font-size: 16px;
                text-align: center;
                font-weight: bold;
            }}
        """)
        self.hotkey_input.setText(f"Current: {self.current_hotkey}")
    
    def register_hotkey(self, hotkey):
        """Регистрируем глобальный хоткей через keyboard"""
        try:
            # Удаляем старый хоткей
            if self.current_hotkey_handler:
                keyboard.remove_hotkey(self.current_hotkey_handler)
            
            # Регистрируем новый
            self.current_hotkey_handler = keyboard.add_hotkey(
                hotkey, 
                self.on_global_hotkey,
                suppress=False
            )
            self.active_hotkey_label.setText(f"Active hotkey: {hotkey}")
            return True
        except Exception as e:
            print(f"Failed to register hotkey {hotkey}: {e}")
            return False
    
    def on_global_hotkey(self):
        """Вызывается при глобальном нажатии хоткея"""
        if self.parent_window:
            QTimer.singleShot(0, self.parent_window.toggle_visibility)
    
    def update_hotkey(self, hotkey):
        """Обновляем хоткей"""
        if self.register_hotkey(hotkey):
            self.current_hotkey = hotkey
            self.hotkey_input.setText(f"Current: {self.current_hotkey}")
            self.hotkeyChanged.emit(hotkey)
    
    def reset_hotkey(self):
        """Сброс на стандартный хоткей"""
        self.stop_listening()
        self.update_hotkey("`")
    
    def toggle_overlay_visibility(self):
        """Переключаем видимость основного окна"""
        if self.parent_window:
            self.parent_window.toggle_visibility()
            self.update_status_label()
    
    def update_status_label(self):
        """Обновляем статус видимости"""
        if self.parent_window and self.parent_window.isVisible():
            self.status_label.setText("● OVERLAY VISIBLE")
            self.status_label.setStyleSheet(f"color: {Theme.SUCCESS}; font-size: 13px; font-weight: bold;")
            self.toggle_btn.setText("HIDE OVERLAY")
        else:
            self.status_label.setText("○ OVERLAY HIDDEN")
            self.status_label.setStyleSheet(f"color: {Theme.WARNING}; font-size: 13px; font-weight: bold;")
            self.toggle_btn.setText("SHOW OVERLAY")
    
    def show_settings(self):
        """Показываем окно настроек"""
        self.update_status_label()
        if self.parent_window:
            x = self.parent_window.x() + (self.parent_window.width() - self.width()) // 2
            y = self.parent_window.y() + (self.parent_window.height() - self.height()) // 2
            self.move(x, y)
        self.show()
        self.raise_()
        self.activateWindow()
    
    def hide_settings(self):
        """Скрываем окно настроек"""
        self.stop_listening()
        self.hide()
        self.closed.emit()
    
    def closeEvent(self, event):
        self.stop_listening()
        self.hide()
        event.accept()
    
    def __del__(self):
        """Очистка при удалении"""
        try:
            self.stop_listening()
            if self.current_hotkey_handler:
                keyboard.remove_hotkey(self.current_hotkey_handler)
        except:
            pass