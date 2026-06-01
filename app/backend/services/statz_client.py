from app.backend.core.config import settings
from app.backend.services.convector import convector_id
import httpx
from app.backend.core.constants import STRATZ_API_URL

class Statz_service:
    @staticmethod
    async def get_by_id(steam_id: int):
        statz_id = convector_id(steam_id)
        query = f"""
            query {{
                player(steamAccountId: {statz_id}) {{
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

        async with httpx.AsyncClient() as client:
            response = await client.post(STRATZ_API_URL, json={"query": query}, headers=headers)
        data = response.json()
        
        player = data.get("data", {}).get("player", {})
        steam_account = player.get("steamAccount", {})
        
        return {
            "steamAccountId": player.get("steamAccountId"),
            "matchCount": player.get("matchCount"),
            "winCount": player.get("winCount"),
            "behaviorScore": player.get("behaviorScore"),
            "name": steam_account.get("name"),
            "avatar": steam_account.get("avatar"),
            "countryCode": steam_account.get("countryCode"),
        }