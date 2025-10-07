from sqlalchemy.ext.asyncio import AsyncSession
from app.cruds.games import GamesCRUD
from app.cruds.players import PlayersCRUD
from app.models.games import GameStatus
from datetime import datetime
import uuid


class WebSocketService:
    def __init__(self):
        self.games_crud = GamesCRUD()
        self.players_crud = PlayersCRUD()

    async def handle_shot(self, game_sid: uuid.UUID, player_sid: uuid.UUID, x: int, y: int, session: AsyncSession):
        game = await self.games_crud.get_game_by_sid(game_sid, session)
        if not game:
            return {"error": "Game not found"}

        if game.status != GameStatus.active:
            return {"error": "Game is not active"}

        if game.current_turn_sid != player_sid:
            return {"error": "Not your turn"}

        target_player_sid = game.player2_sid if player_sid == game.player1_sid else game.player1_sid

        board_cell = await self.games_crud.get_board_cell(game_sid, target_player_sid, x, y, session)

        if board_cell and board_cell.is_ship:
            board_cell.is_hit = True
            result = "HIT"

            ship_destroyed = await self._check_ship_destroyed(game_sid, target_player_sid, x, y, session)
            if ship_destroyed:
                result = "KILL"

            game_over = await self._check_game_over(game_sid, target_player_sid, session)
            if game_over:
                game.status = GameStatus.finished
                game.winner_sid = player_sid
                result = "WIN"
        else:
            result = "MISS"
            game.current_turn_sid = target_player_sid

        await session.commit()

        return {
            "result": result,
            "x": x,
            "y": y,
            "next_turn": game.current_turn_sid,
            "game_over": game.status == GameStatus.finished,
            "winner": game.winner_sid if game.status == GameStatus.finished else None
        }

    async def _check_ship_destroyed(self, game_sid: uuid.UUID, player_sid: uuid.UUID, x: int, y: int, session: AsyncSession):
        return True

    async def _check_game_over(self, game_sid: uuid.UUID, player_sid: uuid.UUID, session: AsyncSession):
        ships = await self.games_crud.get_player_ships(game_sid, player_sid, session)
        return all(ship.is_hit for ship in ships)

    async def start_game(self, game_sid: uuid.UUID, session: AsyncSession):
        game = await self.games_crud.get_game_by_sid(game_sid, session)
        if game and game.status == GameStatus.waiting:
            game.status = GameStatus.active
            await session.commit()
            return True
        return False

    async def surrender_game(self, game_sid: uuid.UUID, player_sid: uuid.UUID, session: AsyncSession):
        game = await self.games_crud.get_game_by_sid(game_sid, session)
        if not game:
            return None

        if game.status != GameStatus.active and game.status != GameStatus.waiting:
            return None

        if player_sid == game.player1_sid:
            winner_sid = game.player2_sid
        else:
            winner_sid = game.player1_sid

        game.status = GameStatus.finished
        game.winner_sid = winner_sid
        game.finished_at = datetime.utcnow()

        await session.commit()
        return winner_sid