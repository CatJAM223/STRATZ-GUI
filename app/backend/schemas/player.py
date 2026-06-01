from pydantic import BaseModel, computed_field
from typing import Optional

class PlayerSchemas(BaseModel):
    steamAccountId: int
    name: Optional[str]
    avatar: Optional[str]
    countryCode: Optional[str]
    matchCount: Optional[int]
    winCount: Optional[int] 
    behaviorScore: Optional[int] 
    
    @computed_field
    @property
    def winrate(self) -> Optional[float]:
        if self.matchCount and self.winCount and self.matchCount > 0:
            return round(self.winCount / self.matchCount * 100, 1)
        return None
