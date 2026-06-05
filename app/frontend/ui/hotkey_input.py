from PyQt6.QtWidgets import QLineEdit
from PyQt6.QtCore import pyqtSignal, Qt

from services.hotkey_manager import hotkey_from_qt_key, format_hotkey_display
from styles.theme import Theme


class HotkeyInput(QLineEdit):
    keyCaptured = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._listening = False
        self.setReadOnly(True)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    def start_listening(self) -> None:
        self._listening = True
        self.clear()
        self.setPlaceholderText("Press key combination...")
        self.setFocus()
        self._apply_style(active=True)

    def stop_listening(self, hotkey: str) -> None:
        self._listening = False
        self.setText(f"Current: {format_hotkey_display(hotkey)}")
        self.setPlaceholderText("Click here and press any key...")
        self._apply_style(active=False)

    def is_listening(self) -> bool:
        return self._listening

    def keyPressEvent(self, event):
        if not self._listening:
            super().keyPressEvent(event)
            return

        hotkey = hotkey_from_qt_key(event)
        if hotkey:
            self.keyCaptured.emit(hotkey)
            event.accept()
            return

        event.accept()

    def _apply_style(self, active: bool) -> None:
        if active:
            self.setStyleSheet(f"""
                QLineEdit {{
                    background: {Theme.ACCENT};
                    border: 2px solid {Theme.ACCENT};
                    border-radius: 12px;
                    padding: 15px;
                    color: {Theme.TEXT};
                    font-size: 16px;
                    font-weight: bold;
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QLineEdit {{
                    background: {Theme.CARD};
                    border: 2px solid {Theme.ACCENT};
                    border-radius: 12px;
                    padding: 15px;
                    color: {Theme.TEXT};
                    font-size: 16px;
                    font-weight: bold;
                }}
            """)
