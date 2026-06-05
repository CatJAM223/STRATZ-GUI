from PyQt6.QtCore import QObject, pyqtSignal, QUrl
from PyQt6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
import json


class ApiClient(QObject):
    """Клиент для связи с FastAPI бэкендом"""

    playerLoaded = pyqtSignal(dict)
    errorOccurred = pyqtSignal(str)
    
    def __init__(self, base_url="http://localhost:8001"):
        super().__init__()
        self.base_url = base_url
        self.network_manager = QNetworkAccessManager()
        self.network_manager.finished.connect(self.on_response)
        self.current_reply = None
        self.current_nickname = ""
    
    def fetch_player(self, nickname):
        """Поиск игрока по Steam ID"""
        self.current_nickname = nickname
        
        try:
            # Если ник - число, используем как steam_id
            steam_id = int(nickname)
            self._fetch_player_by_id(steam_id)
        except ValueError:
            # Если не число - ошибка
            self.errorOccurred.emit(f"Please enter numeric Steam ID (e.g., 76561198356190078)")
    
    def _fetch_player_by_id(self, steam_id):
        """Запрос к вашему API: GET /player/{steam_id}"""
        url = f"{self.base_url}/player/{steam_id}"  # Изменено с POST на GET
        request = QNetworkRequest(QUrl(url))
        request.setHeader(QNetworkRequest.KnownHeaders.ContentTypeHeader, "application/json")
        
        # Используем GET вместо POST
        self.current_reply = self.network_manager.get(request)
    
    def check_api_health(self):
        """Проверка здоровья вашего бэкенда: GET /health/check"""
        url = f"{self.base_url}/health/check"
        request = QNetworkRequest(QUrl(url))
        self.current_reply = self.network_manager.get(request)
        return self.current_reply
    
    def on_response(self, reply):
        """Обработка ответа от сервера"""
        if reply.error() != QNetworkReply.NetworkError.NoError:
            self.errorOccurred.emit(f"Network error: {reply.errorString()}")
            reply.deleteLater()
            return
        
        status_code = reply.attribute(QNetworkRequest.Attribute.HttpStatusCodeAttribute)
        data = reply.readAll().data()
        reply.deleteLater()
        
        try:
            response_data = json.loads(data.decode('utf-8'))
            
            # Проверяем, это ответ от /health/check или от /player/{id}
            if "Сервер работает исправно" in str(response_data):
                # Это ответ health check, обрабатывается в ApiChecker
                return response_data

            if status_code and int(status_code) >= 400:
                detail = response_data.get("detail", "Unknown server error")
                self.errorOccurred.emit(f"Server error ({status_code}): {detail}")
                return
            
            # Это ответ от player endpoint
            self._process_player_data(response_data)
                
        except json.JSONDecodeError as e:
            self.errorOccurred.emit(f"Failed to parse response: {e}")
    
    def _process_player_data(self, data):
        """Преобразуем данные из вашего API в формат для фронтенда"""
        # Данные от бэкенда приходят в camelCase
        player_data = {
            "nickname": data.get("name", str(data.get("steamAccountId", "Unknown"))),
            "steam_id": data.get("steamAccountId"),
            "mmr": 0,  # API не возвращает MMR
            "matches": data.get("matchCount", 0),
            "wins": data.get("winCount", 0),
            "losses": data.get("losses", 0),  # computed field из схемы
            "winrate": data.get("winrate", "0%"),  # computed field из схемы
            "hero": "Unknown",  # API не возвращает топ героя
            "region": data.get("countryCode", "Unknown"),
            "avatar": data.get("avatar", ""),
            "behavior_score": data.get("behaviorScore", 0)
        }
        
        # Форматируем winrate
        if isinstance(player_data["winrate"], (int, float)):
            player_data["winrate"] = f"{player_data['winrate']}%"
        elif player_data["winrate"] is None:
            player_data["winrate"] = "0%"
        
        self.playerLoaded.emit(player_data)