from fastapi import APIRouter, HTTPException
from app.backend.services.statz_client import Statz_service
from app.backend.schemas.player import PlayerSchemas

router = APIRouter(prefix='/player', tags=["player"])

@router.get("/{steam_id:int}", response_model=PlayerSchemas)
async def get_player(steam_id: int):
    result = await Statz_service.get_by_id(steam_id)
    if not result:
        raise HTTPException(status_code=404, detail="Player not found")
    return result

@router.post("/test/{steam_id:int}", response_model=PlayerSchemas)
async def test(steam_id: int):
    result = await Statz_service.get_by_id(steam_id)
    if not result:
        raise HTTPException(status_code=404, detail="Player not found")
    return result