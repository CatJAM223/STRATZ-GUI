from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGraphicsOpacityEffect
from PyQt6.QtCore import QPropertyAnimation, QEasingCurve, pyqtSignal, Qt
from ui.spinner import Spinner
from styles.theme import Theme


class LoadingOverlay(QWidget):
    finished = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.spinner = Spinner()
        
        self.label = QLabel("Loading player data...")
        self.label.setStyleSheet(f"color: {Theme.MUTED}; font-size: 14px; margin-top: 16px;")
        
        layout.addWidget(self.spinner, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.label, alignment=Qt.AlignmentFlag.AlignCenter)
        
        self.opacity_effect = QGraphicsOpacityEffect()
        self.setGraphicsEffect(self.opacity_effect)
        
        self.opacity_anim = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.opacity_anim.setDuration(300)
        self.opacity_anim.setEasingCurve(QEasingCurve.Type.InOutCubic)
        
        self.setFixedSize(200, 150)
        self.hide()
    
    def show_with_animation(self):
        self.spinner.start()
        self.show()
        self.opacity_anim.stop()
        self.opacity_anim.setStartValue(0)
        self.opacity_anim.setEndValue(1)
        self.opacity_anim.start()
    
    def hide_with_animation(self):
        self.opacity_anim.stop()
        self.opacity_anim.setStartValue(1)
        self.opacity_anim.setEndValue(0)
        # Отключаем старые соединения чтобы избежать дублирования
        try:
            self.opacity_anim.finished.disconnect()
        except:
            pass
        self.opacity_anim.finished.connect(self._on_hide_finished)
        self.opacity_anim.start()
    
    def _on_hide_finished(self):
        self.hide()
        self.spinner.stop()
        try:
            self.opacity_anim.finished.disconnect(self._on_hide_finished)
        except:
            pass
    
    def closeEvent(self, event):
        """Очищаем ресурсы при закрытии"""
        self.spinner.stop()
        event.accept()