from PyQt6.QtWidgets import QWidget, QPushButton, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt, QPoint


class TitleBar(QWidget):

    def __init__(self, parent):
        super().__init__(parent)
        
        self.parent = parent
        self.drag_pos = None

        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 14, 20, 14)

        self.title = QLabel("STRATZ OVERLAY")
        self.title.setStyleSheet("color:#6B7280; font-family: 'Bahnschrift'; font-weight: 600; font-size: 11px; letter-spacing: 2px;")

        # Window controls
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(8)
        
        self.settings_btn = QPushButton("⚙")
        self.settings_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.settings_btn.clicked.connect(self.parent.show_settings)
        
        self.minimize_btn = QPushButton("─")
        self.minimize_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.minimize_btn.clicked.connect(self.parent.showMinimized)
        
        self.close_btn = QPushButton("✕")
        self.close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.close_btn.clicked.connect(self.parent.close)

        btn_style = """
            QPushButton {
                background: transparent;
                color: #6B7280;
                border: none;
                font-size: 14px;
                padding: 4px 10px;
                border-radius: 6px;
            }
            QPushButton:hover {
                background: rgba(79, 140, 255, 20);
                color: #4F8CFF;
            }
        """
        
        self.settings_btn.setStyleSheet(btn_style)
        self.minimize_btn.setStyleSheet(btn_style)
        
        self.close_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #6B7280;
                border: none;
                font-size: 14px;
                padding: 4px 10px;
                border-radius: 6px;
            }
            QPushButton:hover {
                background: #EF4444;
                color: white;
            }
        """)

        controls_layout.addWidget(self.settings_btn)
        controls_layout.addWidget(self.minimize_btn)
        controls_layout.addWidget(self.close_btn)

        layout.addWidget(self.title)
        layout.addStretch()
        layout.addLayout(controls_layout)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if self.drag_pos is not None:
            delta = event.globalPosition().toPoint() - self.drag_pos
            self.parent.move(self.parent.pos() + delta)
            self.drag_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event):
        self.drag_pos = None