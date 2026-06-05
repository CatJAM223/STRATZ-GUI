from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QGraphicsDropShadowEffect
from PyQt6.QtCore import QPropertyAnimation, QEasingCurve, Qt
from PyQt6.QtGui import QColor
from styles.theme import Theme
from styles.fonts import display_font, value_font, FONT_FAMILY


class StatCard(QWidget):

    def __init__(self, title):
        super().__init__()

        layout = QVBoxLayout(self)
        layout.setSpacing(8)

        self.title_label = QLabel(title)
        self.title_label.setFont(display_font(11))
        self.title_label.setStyleSheet(f"color: {Theme.MUTED}; font-family: '{FONT_FAMILY}';")
        
        self.value_label = QLabel("---")
        self.value_label.setFont(value_font(26))
        value_color = Theme.SUCCESS if title == "WINRATE" else Theme.TEXT
        self.value_label.setStyleSheet(f"color: {value_color}; font-family: '{FONT_FAMILY}';")

        layout.addWidget(self.title_label)
        layout.addWidget(self.value_label)
        layout.addStretch()

        self.setStyleSheet(f"""
            background: {Theme.CARD};
            border-radius: 14px;
            padding: 14px;
        """)

        # Только один эффект - тень
        self.shadow = QGraphicsDropShadowEffect()
        self.shadow.setBlurRadius(15)
        self.shadow.setOffset(0, 3)
        self.shadow.setColor(QColor(0, 0, 0, 120))
        self.setGraphicsEffect(self.shadow)
        
        # Анимация появления через изменение прозрачности всего виджета
        self.setWindowOpacity(0)
        self.appear_anim = QPropertyAnimation(self, b"windowOpacity")
        self.appear_anim.setDuration(350)
        self.appear_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.appear_anim.setStartValue(0)
        self.appear_anim.setEndValue(1)

    def set_value(self, v):
        self.value_label.setText(str(v))
        self.appear_anim.stop()
        self.appear_anim.start()

    def enterEvent(self, event):
        self.shadow.setBlurRadius(25)
        self.shadow.setOffset(0, 6)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.shadow.setBlurRadius(15)
        self.shadow.setOffset(0, 3)
        super().leaveEvent(event)