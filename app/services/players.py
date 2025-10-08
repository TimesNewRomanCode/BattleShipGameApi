import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from app.cruds.players import PlayersCRUD


class PlayersService:
    def __init__(self):
        self.players_crud = PlayersCRUD()

    async def players_not_game_info(self, session: AsyncSession):
        return await self.players_crud.get_players_by_not_play(session)

    async def get_player_stats(self, player_sid: uuid.UUID, session: AsyncSession):
        games = await self.players_crud.get_player_stats(player_sid, session)

        stats = {"total_games": len(games), "wins": 0, "losses": 0, "games": []}

        for game in games:
            is_winner = game.winner_sid == player_sid
            if is_winner:
                stats["wins"] += 1
            else:
                stats["losses"] += 1

            stats["games"].append(
                {
                    "game_sid": str(game.sid),
                    "opponent": (
                        str(game.player2_sid)
                        if game.player1_sid == player_sid
                        else str(game.player1_sid)
                    ),
                    "result": "win" if is_winner else "loss",
                    "date": game.created_at.isoformat() if game.created_at else None,
                }
            )

        return stats
