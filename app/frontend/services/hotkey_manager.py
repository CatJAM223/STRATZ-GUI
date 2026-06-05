import ctypes
import json
import sys
from ctypes import wintypes
from pathlib import Path

from PyQt6.QtCore import QObject, pyqtSignal, QAbstractNativeEventFilter, Qt

user32 = ctypes.windll.user32
WM_HOTKEY = 0x0312
MOD_NOREPEAT = 0x4000

MODIFIERS = {
    "ctrl": 0x0002,
    "alt": 0x0001,
    "shift": 0x0004,
    "win": 0x0008,
}

VK_CODES = {
    **{f"f{i}": 0x6F + i for i in range(1, 13)},
    **{chr(c): c for c in range(ord("a"), ord("z") + 1)},
    **{str(i): ord("0") + i for i in range(0, 10)},
    "insert": 0x2D,
    "delete": 0x2E,
    "home": 0x24,
    "end": 0x23,
    "pageup": 0x21,
    "pagedown": 0x22,
    "space": 0x20,
    "tab": 0x09,
    "escape": 0x1B,
    "pause": 0x13,
    "printscreen": 0x2C,
}

QT_KEY_MAP = {
    Qt.Key.Key_F1: "f1", Qt.Key.Key_F2: "f2", Qt.Key.Key_F3: "f3",
    Qt.Key.Key_F4: "f4", Qt.Key.Key_F5: "f5", Qt.Key.Key_F6: "f6",
    Qt.Key.Key_F7: "f7", Qt.Key.Key_F8: "f8", Qt.Key.Key_F9: "f9",
    Qt.Key.Key_F10: "f10", Qt.Key.Key_F11: "f11", Qt.Key.Key_F12: "f12",
    Qt.Key.Key_Insert: "insert", Qt.Key.Key_Delete: "delete",
    Qt.Key.Key_Home: "home", Qt.Key.Key_End: "end",
    Qt.Key.Key_PageUp: "pageup", Qt.Key.Key_PageDown: "pagedown",
    Qt.Key.Key_Space: "space", Qt.Key.Key_Tab: "tab",
    Qt.Key.Key_Escape: "escape", Qt.Key.Key_Pause: "pause",
    Qt.Key.Key_Print: "printscreen",
    **{Qt.Key.Key_0 + i: str(i) for i in range(10)},
    **{Qt.Key.Key_A + i: chr(ord("a") + i) for i in range(26)},
}

DEFAULT_HOTKEY = "f9"
HOTKEY_ID = 1
SETTINGS_FILE = Path(__file__).resolve().parents[3] / "settings.json"


def parse_hotkey(hotkey: str) -> tuple[int, int]:
    parts = [p.strip().lower() for p in hotkey.split("+") if p.strip()]
    if not parts:
        raise ValueError("Empty hotkey")

    mods = MOD_NOREPEAT
    key_name = None

    for part in parts:
        if part in MODIFIERS:
            mods |= MODIFIERS[part]
        elif key_name is None:
            key_name = part
        else:
            raise ValueError(f"Invalid hotkey: {hotkey}")

    if key_name is None:
        raise ValueError(f"No key in hotkey: {hotkey}")

    vk = VK_CODES.get(key_name)
    if vk is None:
        raise ValueError(f"Unsupported key: {key_name}")

    return mods, vk


def hotkey_from_qt_key(event) -> str | None:
    key = event.key()
    if key in (Qt.Key.Key_Control, Qt.Key.Key_Alt, Qt.Key.Key_Shift,
               Qt.Key.Key_Meta, Qt.Key.Key_AltGr):
        return None

    key_name = QT_KEY_MAP.get(key)
    if key_name is None:
        text = event.text().strip().lower()
        if len(text) == 1 and text.isalnum():
            key_name = text
        else:
            return None

    parts = []
    modifiers = event.modifiers()
    if modifiers & Qt.KeyboardModifier.ControlModifier:
        parts.append("ctrl")
    if modifiers & Qt.KeyboardModifier.AltModifier:
        parts.append("alt")
    if modifiers & Qt.KeyboardModifier.ShiftModifier:
        parts.append("shift")
    if modifiers & Qt.KeyboardModifier.MetaModifier:
        parts.append("win")

    parts.append(key_name)
    return "+".join(parts)


def format_hotkey_display(hotkey: str) -> str:
    return hotkey.replace("+", " + ").upper()


def load_hotkey() -> str:
    try:
        if SETTINGS_FILE.exists():
            data = json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
            hotkey = data.get("hotkey", DEFAULT_HOTKEY)
            parse_hotkey(hotkey)
            return hotkey
    except (json.JSONDecodeError, ValueError, OSError):
        pass
    return DEFAULT_HOTKEY


def save_hotkey(hotkey: str) -> None:
    SETTINGS_FILE.write_text(
        json.dumps({"hotkey": hotkey}, indent=2),
        encoding="utf-8",
    )


class _NativeHotkeyFilter(QAbstractNativeEventFilter):
    def __init__(self, callback):
        super().__init__()
        self._callback = callback

    def nativeEventFilter(self, eventType, message):
        if sys.platform != "win32" or eventType != b"windows_generic_MSG":
            return False, 0

        msg = wintypes.MSG.from_address(int(message))
        if msg.message == WM_HOTKEY and msg.wParam == HOTKEY_ID:
            self._callback()
            return True, 0
        return False, 0


class HotkeyManager(QObject):
    toggled = pyqtSignal()
    registrationFailed = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._hwnd = 0
        self._filter = None
        self._current_hotkey = DEFAULT_HOTKEY
        self._registered = False

    @property
    def current_hotkey(self) -> str:
        return self._current_hotkey

    def attach_to_window(self, window) -> None:
        from PyQt6.QtWidgets import QApplication

        self._hwnd = int(window.winId())
        if self._filter is None:
            self._filter = _NativeHotkeyFilter(self._on_hotkey_pressed)
            QApplication.instance().installNativeEventFilter(self._filter)

        saved = load_hotkey()
        if not self.register(saved):
            self.register(DEFAULT_HOTKEY)

    def register(self, hotkey: str) -> bool:
        if sys.platform != "win32":
            self.registrationFailed.emit("Global hotkeys are supported on Windows only")
            return False

        if not self._hwnd:
            self.registrationFailed.emit("Window is not ready for hotkey registration")
            return False

        self.unregister()

        try:
            mods, vk = parse_hotkey(hotkey)
        except ValueError as exc:
            self.registrationFailed.emit(str(exc))
            return False

        if not user32.RegisterHotKey(self._hwnd, HOTKEY_ID, mods, vk):
            self.registrationFailed.emit(
                f"Failed to register '{format_hotkey_display(hotkey)}'. "
                "The combination may already be used by another app."
            )
            return False

        self._current_hotkey = hotkey
        self._registered = True
        save_hotkey(hotkey)
        return True

    def unregister(self) -> None:
        if self._registered and self._hwnd:
            user32.UnregisterHotKey(self._hwnd, HOTKEY_ID)
            self._registered = False

    def _on_hotkey_pressed(self) -> None:
        self.toggled.emit()
