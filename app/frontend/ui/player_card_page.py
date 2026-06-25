from PyQt6.QtWidgets import QWidget, QVBoxLayout, QGridLayout, QLabel, QScrollArea, QHBoxLayout
from PyQt6.QtCore import pyqtSignal, Qt, QTimer
from ui.stat_card import StatCard
from ui.animated_button import AnimatedButton
from ui.image_loader import ImageLoader
from styles.theme import Theme
from styles.fonts import heading_font

class PlayerCardPage(QWidget):

    closeRequested = pyqtSignal()
    refreshRequested = pyqtSignal()
    backToSearchRequested = pyqtSignal()

    def __init__(self):
        super().__init__()

        self.current_name = ""
        self.current_steam_id = None

        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        
        # Scroll area for content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                background: transparent;
                border: none;
            }
        """)
        
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setSpacing(24)

        header_layout = QHBoxLayout()
        header_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.setSpacing(20)
        
        self.avatar = ImageLoader()
        self.avatar.setFixedSize(80, 80)
        self.avatar.setStyleSheet("border-radius: 40px; background: #161922;")
        
        self.name_label = QLabel("Player")
        self.name_label.setFont(heading_font(26))
        self.name_label.setStyleSheet(f"""
            color: {Theme.TEXT};
            background: transparent;
        """)
        
        header_layout.addWidget(self.avatar)
        header_layout.addWidget(self.name_label)

        grid = QGridLayout()
        grid.setSpacing(14)
        grid.setContentsMargins(0, 0, 0, 0)

        self.cards = {
            "matches": StatCard("MATCHES"),
            "wins": StatCard("WINS"),
            "losses": StatCard("LOSSES"),
            "winrate": StatCard("WINRATE"),
            "hero": StatCard("TOP HERO"),  # Здесь будет один герой
            "region": StatCard("REGION"),
        }

        positions = [(0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (1, 2)]
        for (key, card), (row, col) in zip(self.cards.items(), positions):
            grid.addWidget(card, row, col)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(12)
        
        self.back_btn = AnimatedButton("← BACK TO SEARCH", "secondary")
        self.refresh_btn = AnimatedButton("⟳ REFRESH", "secondary")
        self.close_btn = AnimatedButton("✕ CLOSE", "primary")

        self.back_btn.clicked.connect(self.backToSearchRequested.emit)
        self.refresh_btn.clicked.connect(self.refreshRequested.emit)
        self.close_btn.clicked.connect(self._on_close_clicked)

        button_layout.addWidget(self.back_btn)
        button_layout.addWidget(self.refresh_btn)
        button_layout.addWidget(self.close_btn)

        layout.addLayout(header_layout)
        layout.addLayout(grid)
        layout.addLayout(button_layout)
        layout.addStretch()
        
        scroll.setWidget(content)
        main_layout.addWidget(scroll)

    def _on_close_clicked(self):
        self.closeRequested.emit()

    def set_player_data(self, data):
        self.current_steam_id = data.get("steam_id")
        self.current_name = data.get("nickname", "")
        self.name_label.setText(self.current_name)
        
        avatar_url = data.get("avatar", "")
        if avatar_url:
            self.avatar.load_image(avatar_url)
        else:
            self.avatar.setText("🎮")
        
        cards_data = {
            "matches": data.get("matches", 0),
            "wins": data.get("wins", 0),
            "losses": data.get("losses", 0),
            "winrate": data.get("winrate", "0%"),
            "hero": data.get("hero", "No data"),
            "region": data.get("region", "Unknown"),
        }
        
        self._animate_cards_sequential(cards_data)
    
    def _animate_cards_sequential(self, data):
        """Animate cards appearing one by one"""
        cards_list = list(self.cards.items())
        
        def animate_card(index=0):
            if index >= len(cards_list):
                return
            
            key, card = cards_list[index]
            value = data.get(key, "---")
            card.set_value(value)
            QTimer.singleShot(60, lambda: animate_card(index + 1))
        
        animate_card()