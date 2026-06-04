from PyQt6.QtWidgets import QLabel
from PyQt6.QtCore import QTimer, Qt


class Spinner(QLabel):

    def __init__(self):
        super().__init__()

        self.frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧"]
        self.index = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet("font-size: 48px; color: #4F8CFF;")
        self.hide()

    def start(self):
        if not self.timer.isActive():
            self.index = 0
            self.show()
            self.timer.start(80)

    def stop(self):
        if self.timer.isActive():
            self.timer.stop()
        self.hide()
        self.setText("")  # Очищаем текст

    def update_frame(self):
        if self.isVisible():  # Проверяем, виден ли спиннер
            self.setText(self.frames[self.index])
            self.index = (self.index + 1) % len(self.frames)