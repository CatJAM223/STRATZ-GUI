# app/backend/services/statz_client.py

from app.backend.core.config import settings
from app.backend.services.convector import normalize_steam_id
import httpx
from app.backend.core.constants import STRATZ_API_URL
from collections import Counter


class Statz_service:
    @staticmethod
    async def get_by_id(steam_id: int):
        account_id = normalize_steam_id(steam_id)
        query = f"""
            query {{
                player(steamAccountId: {account_id}) {{
                    steamAccountId
                    matchCount
                    winCount
                    imp
                    behaviorScore
                    firstMatchDate
                    lastMatchDate
                    steamAccount {{
                        name
                        avatar
                        countryCode
                    }}
                }}
            }}
        """
        headers = {
            "Authorization": f"Bearer {settings.STRATZ_TOKEN}",
            "User-Agent": "STRATZ_API",
            "Content-Type": "application/json"
        }

        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(STRATZ_API_URL, json={"query": query}, headers=headers)
        
        if response.status_code != 200:
            return None
            
        data = response.json()

        if data.get("errors"):
            return None

        player = data.get("data", {}).get("player")
        if not player or player.get("matchCount") is None:
            return None

        steam_account = player.get("steamAccount") or {}
        
        return {
            "steamAccountId": player.get("steamAccountId"),
            "matchCount": player.get("matchCount"),
            "winCount": player.get("winCount"),
            "behaviorScore": player.get("behaviorScore"),
            "name": steam_account.get("name"),
            "avatar": steam_account.get("avatar"),
            "countryCode": steam_account.get("countryCode"),
        }
    
    @staticmethod
    async def get_best_hero(steam_id: int, limit: int = 100):
        """
        Получает самого частого героя игрока
        
        Args:
            steam_id: ID игрока в Steam
            limit: количество последних матчей для анализа
        
        Returns:
            str: Имя самого частого героя или None
        """
        account_id = normalize_steam_id(steam_id)
        
        query = f"""
            query {{
                player(steamAccountId: {account_id}) {{
                    matches(
                        request: {{
                            take: {limit}
                            orderBy: DESC
                        }}
                    ) {{
                        players(steamAccountId: {account_id}) {{
                            hero {{
                                displayName
                            }}
                        }}
                    }}
                }}
            }}
        """
        
        headers = {
            "Authorization": f"Bearer {settings.STRATZ_TOKEN}",
            "User-Agent": "STRATZ_API",
            "Content-Type": "application/json"
        }
        
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(STRATZ_API_URL, json={"query": query}, headers=headers)
        
        if response.status_code != 200:
            return None
            
        data = response.json()
        
        if data.get("errors"):
            return None
            
        player = data.get("data", {}).get("player")
        if not player:
            return None
            
        matches = player.get("matches") or []
        
        heroes = []
        for match in matches:
            players = match.get("players") or []
            for player_data in players:
                hero = player_data.get("hero")
                if hero and hero.get("displayName"):
                    heroes.append(hero.get("displayName"))
        
        if not heroes:
            return None
        
        hero_counter = Counter(heroes)
        top_hero = hero_counter.most_common(1)
        
        return top_hero[0][0] if top_hero else None