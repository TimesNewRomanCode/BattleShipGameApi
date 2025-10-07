from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_session
from app.services.games import GamesService
from app.schemas.games import CreateGameRequest, CreateGameResponse, ActiveGameResponse

router = APIRouter(prefix="/games", tags=["games"])

games_service = GamesService()


@router.post("/create", response_model=CreateGameResponse)
async def create_game(
        request: CreateGameRequest,
        session: AsyncSession = Depends(get_session),
):
    try:
        game = await games_service.create_game_with_boards(
            request.player1_sid,
            request.player2_sid,
            session
        )

        return CreateGameResponse(
            game_sid=game.sid,
            status=game.status.value,
            player1_sid=game.player1_sid,
            player2_sid=game.player2_sid,
            message="Игра успешно создана с расставленными кораблями"
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("", response_model=List[ActiveGameResponse])
async def get_active_games(
        session: AsyncSession = Depends(get_session),
):
    return await games_service.get_active_games_with_boards(session)