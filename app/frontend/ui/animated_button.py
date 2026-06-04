from PyQt6.QtWidgets import QPushButton, QGraphicsDropShadowEffect
from PyQt6.QtCore import QPropertyAnimation, QEasingCurve, QPoint
from PyQt6.QtGui import QColor
from styles.theme import Theme


class AnimatedButton(QPushButton):

    def __init__(self, text="", variant="primary"):
        super().__init__(text)
        
        self.variant = variant
        self.animations_active = True  # Флаг для отключения анимаций при закрытии
        
        if variant == "primary":
            self.setStyleSheet(f"""
                QPushButton {{
                    background: {Theme.ACCENT_GRADIENT};
                    color: {Theme.TEXT};
                    border: none;
                    border-radius: 14px;
                    min-height: 48px;
                    font-weight: 600;
                    font-size: 14px;
                }}
                QPushButton:hover {{
                    background: {Theme.ACCENT_HOVER};
                }}
                QPushButton:pressed {{
                    padding-top: 2px;
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QPushButton {{
                    background: rgba(34, 38, 47, 180);
                    color: {Theme.TEXT};
                    border: 1px solid rgba(79, 140, 255, 50);
                    border-radius: 14px;
                    min-height: 48px;
                    font-weight: 600;
                    font-size: 14px;
                }}
                QPushButton:hover {{
                    background: rgba(79, 140, 255, 30);
                    border: 1px solid {Theme.ACCENT};
                }}
            """)
        
        self.glow = QGraphicsDropShadowEffect()
        self.glow.setBlurRadius(0)
        self.glow.setColor(QColor(79, 140, 255, 0))
        self.glow.setOffset(0, 0)
        self.setGraphicsEffect(self.glow)
        
        self.glow_anim = QPropertyAnimation(self.glow, b"blurRadius")
        self.glow_anim.setDuration(200)
        self.glow_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        self.pos_anim = QPropertyAnimation(self, b"geometry")
        self.pos_anim.setDuration(100)
        self.pos_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
    
    def close_animations(self):
        """Останавливаем все анимации при закрытии"""
        self.animations_active = False
        if self.glow_anim and self.glow_anim.state() == QPropertyAnimation.State.Running:
            self.glow_anim.stop()
        if self.pos_anim and self.pos_anim.state() == QPropertyAnimation.State.Running:
            self.pos_anim.stop()
    
    def enterEvent(self, event):
        if self.animations_active and self.isEnabled():
            self.glow_anim.stop()
            self.glow_anim.setStartValue(0)
            self.glow_anim.setEndValue(20)
            self.glow_anim.start()
            self.glow.setColor(QColor(79, 140, 255, 80))
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        if self.animations_active and self.isEnabled():
            self.glow_anim.stop()
            self.glow_anim.setStartValue(20)
            self.glow_anim.setEndValue(0)
            self.glow_anim.start()
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        if self.animations_active and self.isEnabled():
            geo = self.geometry()
            self.pos_anim.stop()
            self.pos_anim.setStartValue(geo)
            self.pos_anim.setEndValue(geo.adjusted(2, 2, -2, -2))
            self.pos_anim.start()
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if self.animations_active and self.isEnabled():
            self.pos_anim.stop()
            self.pos_anim.setStartValue(self.geometry())
            self.pos_anim.setEndValue(self.geometry().adjusted(-2, -2, 2, 2))
            self.pos_anim.start()
        super().mouseReleaseEvent(event)