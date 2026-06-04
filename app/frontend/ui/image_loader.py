from PyQt6.QtWidgets import QLabel
from PyQt6.QtGui import QPixmap
from PyQt6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
from PyQt6.QtCore import QUrl, pyqtSignal, Qt


class ImageLoader(QLabel):
    loaded = pyqtSignal()
    error = pyqtSignal(str)
    
    def __init__(self, url=None):
        super().__init__()
        self.network_manager = QNetworkAccessManager()
        self.network_manager.finished.connect(self.on_image_loaded)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setText("🎮")  # плейсхолдер
        self.setStyleSheet("font-size: 40px;")
        
        if url:
            self.load_image(url)
    
    def load_image(self, url):
        self.setText("⏳")  # загрузка
        self.setStyleSheet("font-size: 30px;")
        self.network_manager.get(QNetworkRequest(QUrl(url)))
    
    def on_image_loaded(self, reply):
        if reply.error() == QNetworkReply.NetworkError.NoError:
            data = reply.readAll()
            pixmap = QPixmap()
            pixmap.loadFromData(data)
            
            if not pixmap.isNull():
                scaled = pixmap.scaled(
                    self.size(),
                    Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                    Qt.TransformationMode.SmoothTransformation
                )
                self.setPixmap(scaled)
                self.setScaledContents(True)
                self.setText("")  # очищаем текст
                self.loaded.emit()
            else:
                self.setText("❌")
                self.setStyleSheet("font-size: 30px;")
                self.error.emit("Failed to decode image")
        else:
            self.setText("❌")
            self.setStyleSheet("font-size: 30px;")
            self.error.emit(f"Network error: {reply.errorString()}")
        
        reply.deleteLater()