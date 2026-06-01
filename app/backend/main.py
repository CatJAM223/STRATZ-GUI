from fastapi import FastAPI
from app.backend.api.routers.health import router as router_check
from app.backend.api.routers.player import router as router_player

app = FastAPI()

app.include_router(router_check)
app.include_router(router_player)