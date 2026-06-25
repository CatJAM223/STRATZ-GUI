# app/backend/schemas/player.py

from pydantic import BaseModel, computed_field
from typing import Optional

class PlayerSchemas(BaseModel):
    steamAccountId: Optional[int] = None
    name: Optional[str] = None
    avatar: Optional[str] = None
    countryCode: Optional[str] = None
    matchCount: Optional[int] = None
    winCount: Optional[int] = None
    behaviorScore: Optional[int] = None
    top_hero: Optional[str] = None
    
    @computed_field
    @property
    def winrate(self) -> Optional[float]:
        if self.matchCount and self.winCount and self.matchCount > 0:
            return round(self.winCount / self.matchCount * 100, 1)
        return None
    
    @computed_field
    @property
    def losses(self) -> Optional[int]:
        if self.matchCount and self.winCount:
            return self.matchCount - self.winCount
        return None