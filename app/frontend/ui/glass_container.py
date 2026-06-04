from PyQt6.QtWidgets import QWidget, QVBoxLayout


class GlassContainer(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setObjectName("Glass")

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(12)