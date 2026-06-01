from app.backend.core.constants import STEAM_OFFSET

def convector_id(steam_id: int) -> int:
    return steam_id - STEAM_OFFSET