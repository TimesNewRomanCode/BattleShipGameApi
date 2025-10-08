import uuid

from app.services.games import GamesService
from app.services.players import PlayersService
from fastapi import APIRouter, Depends, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.auth import RegistrationScheme, TokenResponse
from app.services.auth import AuthService

from app.core.database import get_session

router = APIRouter(prefix="/players", tags=["players"])

games_service = GamesService()

@router.post("/register")
async def registration(
    data: RegistrationScheme,
    session: AsyncSession = Depends(get_session),
    service: AuthService = Depends(AuthService),
):
    return await service.registration(data, session)


@router.post("/login", response_model=TokenResponse)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_session),
    service: AuthService = Depends(AuthService),
    response: Response = Response(),
):
    return await service.login_for_access_token(form_data, session, response)

@router.get("")
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
