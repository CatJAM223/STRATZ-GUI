from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QLabel, QHBoxLayout
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QFont

from ui.animated_button import AnimatedButton
from styles.theme import Theme


class SearchPage(QWidget):

    searchRequested = pyqtSignal(str)
    checkApiRequested = pyqtSignal()
    settingsRequested = pyqtSignal()

    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(40, 40, 40, 40)

        # Title section
        title_container = QHBoxLayout()
        title_container.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        subtitle = QLabel("PLAYER STATS OVERLAY")
        subtitle_font = QFont()
        subtitle_font.setPointSize(13)
        subtitle_font.setBold(True)
        subtitle.setFont(subtitle_font)
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet(f"color: {Theme.ACCENT}; letter-spacing: 4px;")

        self.input = QLineEdit()
        self.input.setPlaceholderText("Enter player nickname...")
        self.input.returnPressed.connect(self.emit_search)

        # Кнопки в ряд
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(12)
        
        self.search_btn = AnimatedButton("SEARCH", "primary")
        self.check_api_btn = AnimatedButton("CHECK API STATS", "secondary")
        self.settings_btn = AnimatedButton("⚙ SETTINGS", "secondary")

        self.search_btn.clicked.connect(self.emit_search)
        self.check_api_btn.clicked.connect(self.checkApiRequested.emit)
        self.settings_btn.clicked.connect(self.settingsRequested.emit)

        buttons_layout.addWidget(self.search_btn)
        buttons_layout.addWidget(self.check_api_btn)
        buttons_layout.addWidget(self.settings_btn)

        layout.addStretch()
        layout.addLayout(title_container)
        layout.addWidget(subtitle)
        layout.addSpacing(30)
        layout.addWidget(self.input)
        layout.addSpacing(16)
        layout.addLayout(buttons_layout)
        layout.addStretch()

    def emit_search(self):
        nickname = self.input.text().strip()
        if nickname:
            self.searchRequested.emit(nickname)