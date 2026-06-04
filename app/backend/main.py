from fastapi import FastAPI
from app.backend.api.routers.health import router as router_check
from app.backend.api.routers.player import router as router_player

app = FastAPI(title="Dota 2 Player Stats API")

app.include_router(router_check)
app.include_router(router_player)

@app.get("/")
async def root():
    return {"message": "Dota 2 Player Stats API is running"}