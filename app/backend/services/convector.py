from app.backend.core.constants import STEAM_OFFSET


def convector_id(steam_id: int) -> int:
    return steam_id - STEAM_OFFSET


def normalize_steam_id(steam_id: int) -> int:
    """Convert 64-bit Steam ID to 32-bit account ID if needed."""
    if steam_id >= STEAM_OFFSET:
        return convector_id(steam_id)
    return steam_id