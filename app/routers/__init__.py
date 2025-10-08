from fastapi import APIRouter
from .auth import router as auth_router
from .players import router as players_router
from .games import router as games_router
from .websocket import router as websocket_router

router = APIRouter(prefix="")

router.include_router(auth_router)
router.include_router(players_router)
router.include_router(games_router)

router.include_router(websocket_router)
