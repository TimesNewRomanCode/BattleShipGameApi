import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_session
from app.services.games import GamesService
from app.services.players import PlayersService

router = APIRouter(prefix="/players", tags=["players"])

games_service = GamesService()


@router.get("/players")
async def get_available_players(
    session: AsyncSession = Depends(get_session),
    service: PlayersService = Depends(PlayersService),
):
    return await service.players_not_game_info(session)

@router.get("/{player_sid}/stats")
async def get_player_stats(
    player_sid: uuid.UUID,
    session: AsyncSession = Depends(get_session),
    service: PlayersService = Depends(PlayersService),
):
    return await service.get_player_stats(player_sid, session)