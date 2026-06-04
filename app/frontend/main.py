import sys
import signal
from PyQt6.QtWidgets import QApplication
from ui.main_window import MainWindow
from pathlib import Path

def signal_handler(signum, frame):
    """Обработка Ctrl+C для чистого выхода"""
    print("\nGracefully shutting down...")
    QApplication.quit()
    sys.exit(0)

# Устанавливаем обработчик сигнала
signal.signal(signal.SIGINT, signal_handler)

app = QApplication(sys.argv)

style_path = Path(__file__).parent / "styles" / "app.qss"
app.setStyleSheet(style_path.read_text(encoding="utf-8"))

window = MainWindow()
window.show()

sys.exit(app.exec())