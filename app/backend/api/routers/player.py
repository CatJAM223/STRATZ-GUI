from fastapi import APIRouter
from app.backend.services.statz_client import Statz_service
from app.backend.schemas.player import PlayerSchemas

router = APIRouter(prefix='/player', tags=["player"])

@router.post("/test/{steam_id:int}", response_model=PlayerSchemas)
async def test(steam_id: int):
    return await Statz_service.get_by_id(steam_id)