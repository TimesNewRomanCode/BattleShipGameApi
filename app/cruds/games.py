from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.games import Games, GameStatus
from app.models.players import Players
from app.models.boards import Boards
import uuid

class GamesCRUD:
    def __init__(self):
        pass

    async def create_game(self, game: Games, session: AsyncSession):
        session.add(game)
        await session.commit()
        await session.refresh(game)
        return game

    async def get_player_by_sid(self, player_sid: uuid.UUID, session: AsyncSession):
        result = await session.execute(select(Players).where(Players.sid == player_sid))
        return result.scalars().first()

    async def create_board(self, board: Boards, session: AsyncSession):
        session.add(board)
        await session.commit()
        await session.refresh(board)
        return board

    async def get_player_active_games(self, player_sid: uuid.UUID, session: AsyncSession):
        result = await session.execute(
            select(Games).where(
                (Games.player1_sid == player_sid) | (Games.player2_sid == player_sid),
                Games.status.in_([GameStatus.waiting, GameStatus.active])
            )
        )
        return result.scalars().all()

    async def get_active_games_with_boards(self, session: AsyncSession):
        result = await session.execute(
            select(Games).where(
                Games.status.in_([GameStatus.waiting, GameStatus.active])
            )
        )
        games = result.scalars().all()
        return games

    async def get_boards_by_game(self, game_sid: uuid.UUID, session: AsyncSession):
        result = await session.execute(
            select(Boards).where(Boards.game_sid == game_sid)
        )
        return result.scalars().all()

    async def get_board_cell(self, game_sid: uuid.UUID, player_sid: uuid.UUID, x: int, y: int, session: AsyncSession):
        result = await session.execute(
            select(Boards).where(
                Boards.game_sid == game_sid,
                Boards.player_sid == player_sid,
                Boards.x == x,
                Boards.y == y
            )
        )
        return result.scalars().first()

    async def get_player_ships(self, game_sid: uuid.UUID, player_sid: uuid.UUID, session: AsyncSession):
        result = await session.execute(
            select(Boards).where(
                Boards.game_sid == game_sid,
                Boards.player_sid == player_sid,
                Boards.is_ship == True
            )
        )
        return result.scalars().all()

    async def get_game_by_sid(self, game_sid: uuid.UUID, session: AsyncSession):
        result = await session.execute(select(Games).where(Games.sid == game_sid))
        return result.scalars().first()

    async def update_game_status(self, game_sid: uuid.UUID, status: GameStatus, session: AsyncSession):
        game = await self.get_game_by_sid(game_sid, session)
        if game:
            game.status = status
            await session.commit()
        return game

    async def get_player_stats(self, player_sid: uuid.UUID, session: AsyncSession):
        result = await session.execute(
            select(Games).where(
                (Games.player1_sid == player_sid) | (Games.player2_sid == player_sid),
                Games.status == GameStatus.finished
            )
        )
        return result.scalars().all()