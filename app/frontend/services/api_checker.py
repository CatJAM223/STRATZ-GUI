from PyQt6.QtCore import QObject, pyqtSignal, QUrl
from PyQt6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
import json
from datetime import datetime


class ApiChecker(QObject):
    resultReady = pyqtSignal(dict)
    
    def __init__(self, base_url="http://localhost:8001"):
        super().__init__()
        self.base_url = base_url
        self.network_manager = QNetworkAccessManager()
        self.network_manager.finished.connect(self.on_response)
    
    def check_api_status(self):
        """Проверяем статус вашего бэкенда"""
        url = f"{self.base_url}/health/check"
        request = QNetworkRequest(QUrl(url))
        request.setHeader(QNetworkRequest.KnownHeaders.UserAgentHeader, "PyQt6 DotaOverlay/1.0")
        
        self.start_time = datetime.now()
        self.network_manager.get(request)
    
    def on_response(self, reply):
        elapsed = (datetime.now() - self.start_time).total_seconds()
        
        if reply.error() != QNetworkReply.NetworkError.NoError:
            self.resultReady.emit({
                "success": False,
                "message": "❌ Backend server is not responding",
                "details": f"Error: {reply.errorString()}\nTime: {elapsed:.2f}s\n\nMake sure your FastAPI server is running on {self.base_url}"
            })
            reply.deleteLater()
            return
        
        status_code = reply.attribute(QNetworkRequest.Attribute.HttpStatusCodeAttribute)
        data = reply.readAll().data()
        reply.deleteLater()
        
        try:
            response_data = json.loads(data.decode('utf-8'))
            self.resultReady.emit({
                "success": True,
                "message": f"✅ Backend is working! (HTTP {status_code})",
                "details": f"Response time: {elapsed:.2f}s\n\nServer response:\n{json.dumps(response_data, indent=2, ensure_ascii=False)}"
            })
        except json.JSONDecodeError as e:
            self.resultReady.emit({
                "success": False,
                "message": "⚠️ Backend returned invalid data",
                "details": f"Parse error: {e}\nRaw data: {data[:200]}"
            })