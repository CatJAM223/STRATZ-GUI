from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QPushButton
from PyQt6.QtCore import Qt, pyqtSignal, QTimer

from styles.theme import Theme
from ui.animated_button import AnimatedButton
from ui.hotkey_input import HotkeyInput
from services.hotkey_manager import format_hotkey_display, DEFAULT_HOTKEY


class SettingsOverlay(QWidget):
    closed = pyqtSignal()
    hotkeyChanged = pyqtSignal(str)

    def __init__(self, parent=None, hotkey_manager=None):
        super().__init__(parent)

        self.hotkey_manager = hotkey_manager
        self.parent_window = parent

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.setVisible(False)
        self.setFixedSize(500, 420)

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

        title = QLabel("⚙ SETTINGS")
        title.setStyleSheet(
            f"color: {Theme.ACCENT}; font-size: 18px; font-weight: bold; letter-spacing: 2px;"
        )
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        hotkey_label = QLabel("GLOBAL HOTKEY")
        hotkey_label.setStyleSheet(
            f"color: {Theme.TEXT}; font-size: 13px; font-weight: bold; margin-top: 10px;"
        )

        hotkey_desc = QLabel(
            "Click the field and press a key combination to toggle the overlay\n"
            "(Works globally, even when the app is in the background)"
        )
        hotkey_desc.setStyleSheet(f"color: {Theme.MUTED}; font-size: 11px;")
        hotkey_desc.setWordWrap(True)

        self.hotkey_input = HotkeyInput()
        self.hotkey_input.setMinimumHeight(50)
        self.hotkey_input.mousePressEvent = self._on_input_click
        self.hotkey_input.keyCaptured.connect(self._on_hotkey_captured)

        current_hotkey = (
            hotkey_manager.current_hotkey if hotkey_manager else DEFAULT_HOTKEY
        )
        self.hotkey_input.stop_listening(current_hotkey)

        reset_btn = QPushButton(f"Reset to Default ({DEFAULT_HOTKEY.upper()})")
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

        self.status_label = QLabel("● OVERLAY VISIBLE")
        self.status_label.setStyleSheet(
            f"color: {Theme.SUCCESS}; font-size: 13px; font-weight: bold;"
        )
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.active_hotkey_label = QLabel(
            f"Active hotkey: {format_hotkey_display(current_hotkey)}"
        )
        self.active_hotkey_label.setStyleSheet(f"color: {Theme.MUTED}; font-size: 12px;")
        self.active_hotkey_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.hotkey_status_label = QLabel("")
        self.hotkey_status_label.setStyleSheet(f"color: {Theme.ERROR}; font-size: 11px;")
        self.hotkey_status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.hotkey_status_label.setWordWrap(True)

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
        layout.addSpacing(6)
        layout.addWidget(self.active_hotkey_label)
        layout.addWidget(self.hotkey_status_label)
        layout.addSpacing(14)
        layout.addWidget(self.status_label)
        layout.addStretch()
        layout.addLayout(buttons_layout)

        self._listen_timer = QTimer()
        self._listen_timer.setSingleShot(True)
        self._listen_timer.timeout.connect(self._cancel_listening)

        if hotkey_manager:
            hotkey_manager.registrationFailed.connect(self._show_hotkey_error)

    def _on_input_click(self, event):
        self.start_listening()
        event.accept()

    def start_listening(self):
        if self.hotkey_input.is_listening():
            return
        self.hotkey_status_label.setText("")
        self.hotkey_input.start_listening()
        self._listen_timer.start(8000)

    def _cancel_listening(self):
        if not self.hotkey_input.is_listening():
            return
        hotkey = self.hotkey_manager.current_hotkey if self.hotkey_manager else DEFAULT_HOTKEY
        self.hotkey_input.stop_listening(hotkey)

    def _on_hotkey_captured(self, hotkey: str):
        self._listen_timer.stop()
        self.update_hotkey(hotkey)

    def update_hotkey(self, hotkey: str):
        if not self.hotkey_manager:
            return

        if self.hotkey_manager.register(hotkey):
            self.hotkey_input.stop_listening(hotkey)
            self.active_hotkey_label.setText(
                f"Active hotkey: {format_hotkey_display(hotkey)}"
            )
            self.hotkey_status_label.setText("")
            self.hotkeyChanged.emit(hotkey)
        else:
            self.hotkey_input.stop_listening(self.hotkey_manager.current_hotkey)

    def reset_hotkey(self):
        self._listen_timer.stop()
        self.update_hotkey(DEFAULT_HOTKEY)

    def _show_hotkey_error(self, message: str):
        self.hotkey_status_label.setText(message)

    def toggle_overlay_visibility(self):
        if self.parent_window:
            self.parent_window.toggle_visibility()
            self.update_status_label()

    def update_status_label(self):
        if self.parent_window and self.parent_window.isVisible():
            self.status_label.setText("● OVERLAY VISIBLE")
            self.status_label.setStyleSheet(
                f"color: {Theme.SUCCESS}; font-size: 13px; font-weight: bold;"
            )
            self.toggle_btn.setText("HIDE OVERLAY")
        else:
            self.status_label.setText("○ OVERLAY HIDDEN")
            self.status_label.setStyleSheet(
                f"color: {Theme.WARNING}; font-size: 13px; font-weight: bold;"
            )
            self.toggle_btn.setText("SHOW OVERLAY")

    def show_settings(self):
        self.update_status_label()
        if self.hotkey_manager:
            self.active_hotkey_label.setText(
                f"Active hotkey: {format_hotkey_display(self.hotkey_manager.current_hotkey)}"
            )
        if self.parent_window:
            x = self.parent_window.x() + (self.parent_window.width() - self.width()) // 2
            y = self.parent_window.y() + (self.parent_window.height() - self.height()) // 2
            self.move(x, y)
        self.show()
        self.raise_()
        self.activateWindow()

    def hide_settings(self):
        self._listen_timer.stop()
        if self.hotkey_input.is_listening():
            hotkey = self.hotkey_manager.current_hotkey if self.hotkey_manager else DEFAULT_HOTKEY
            self.hotkey_input.stop_listening(hotkey)
        self.hide()
        self.closed.emit()

    def closeEvent(self, event):
        self.hide_settings()
        event.accept()
