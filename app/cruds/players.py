import uuid
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Games
from app.models.games import GameStatus
from app.models.players import Players


class PlayersCRUD:

    async def create_players(self, users: Players, session: AsyncSession):
        session.add(users)
        await session.commit()
        await session.refresh(users)

    async def get_players_by_email(self, email: str, session: AsyncSession):
        result = await session.execute(select(Players).where(Players.email == email))
        return result.scalars().first()

    async def get_players_by_not_play(self, session: AsyncSession):
        active_statuses = [GameStatus.waiting, GameStatus.active]

        subquery = (
            select(Games.player1_sid)
            .where(Games.status.in_(active_statuses))
            .union(select(Games.player2_sid).where(Games.status.in_(active_statuses)))
            .subquery()
        )

        result = await session.execute(
            select(Players.sid, Players.username).where(
                Players.sid.not_in(select(subquery))
            )
        )
        players = result.all()
        return [{"sid": sid, "username": username} for sid, username in players]

    async def get_player_stats(self, player_sid: uuid.UUID, session: AsyncSession):
        result = await session.execute(
            select(Games).where(
                (Games.player1_sid == player_sid) | (Games.player2_sid == player_sid),
                Games.status == GameStatus.finished,
            )
        )
        games = result.scalars().all()
        return games
