from sqlalchemy.ext.asyncio import AsyncSession
from app.cruds.games import GamesCRUD
from app.models.games import Games, GameStatus
from app.models.boards import Boards
import uuid
import random


class GamesService:
    def __init__(self):
        self.games_crud = GamesCRUD()

    async def create_game_with_boards(self, player1_sid: uuid.UUID, player2_sid: uuid.UUID, session: AsyncSession):
        player1 = await self.games_crud.get_player_by_sid(player1_sid, session)
        player2 = await self.games_crud.get_player_by_sid(player2_sid, session)

        if not player1 or not player2:
            raise ValueError("Один из игроков не найден")

        player1_active_games = await self.games_crud.get_player_active_games(player1_sid, session)
        player2_active_games = await self.games_crud.get_player_active_games(player2_sid, session)

        if player1_active_games:
            raise ValueError(f"Игрок {player1.username} уже находится в активной игре")

        if player2_active_games:
            raise ValueError(f"Игрок {player2.username} уже находится в активной игре")

        game = Games(
            player1_sid=player1_sid,
            player2_sid=player2_sid,
            status=GameStatus.waiting,
            current_turn_sid=player1_sid
        )

        game = await self.games_crud.create_game(game, session)

        await self._create_ships_for_player(game.sid, player1_sid, session)
        await self._create_ships_for_player(game.sid, player2_sid, session)

        return game

    async def _create_ships_for_player(self, game_sid: uuid.UUID, player_sid: uuid.UUID, session: AsyncSession):
        ships = self._generate_ships()

        boards = []
        for ship_x, ship_y in ships:
            board = Boards(
                game_sid=game_sid,
                player_sid=player_sid,
                x=ship_x,
                y=ship_y,
                is_ship=True,
                is_hit=False
            )
            boards.append(board)

        session.add_all(boards)
        await session.commit()

    def _generate_ships(self):
        ships = []
        board = [[False for _ in range(10)] for _ in range(10)]

        ship_types = [(1, 4), (2, 3), (3, 2), (4, 1)]

        for count, size in ship_types:
            for _ in range(count):
                ship_coords = self._place_ship(board, size)
                ships.extend(ship_coords)

        return ships

    def _place_ship(self, board, size):
        while True:
            horizontal = random.choice([True, False])

            if horizontal:
                max_x = 10 - size
                max_y = 9
            else:
                max_x = 9
                max_y = 10 - size

            if max_x < 0 or max_y < 0:
                continue

            x = random.randint(0, max_x)
            y = random.randint(0, max_y)

            if self._can_place_ship(board, x, y, size, horizontal):
                ship_coords = []
                for i in range(size):
                    if horizontal:
                        ship_x, ship_y = x + i, y
                    else:
                        ship_x, ship_y = x, y + i

                    board[ship_y][ship_x] = True
                    ship_coords.append((ship_x, ship_y))

                return ship_coords

    def _can_place_ship(self, board, x, y, size, horizontal):
        for i in range(size):
            if horizontal:
                check_x, check_y = x + i, y
            else:
                check_x, check_y = x, y + i

            if check_x >= 10 or check_y >= 10:
                return False

            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    nx, ny = check_x + dx, check_y + dy
                    if 0 <= nx < 10 and 0 <= ny < 10 and board[ny][nx]:
                        return False

        return True

    async def get_active_games_with_boards(self, session: AsyncSession):
        games = await self.games_crud.get_active_games_with_boards(session)

        result = []
        for game in games:
            boards = await self.games_crud.get_boards_by_game(game.sid, session)

            player1_boards = [board for board in boards if board.player_sid == game.player1_sid]
            player2_boards = [board for board in boards if board.player_sid == game.player2_sid]

            game_data = {
                "game_sid": game.sid,
                "status": game.status.value,
                "player1_sid": game.player1_sid,
                "player2_sid": game.player2_sid,
                "current_turn_sid": game.current_turn_sid,
                "boards": {
                    "player1": [
                        {
                            "x": board.x,
                            "y": board.y,
                            "is_ship": board.is_ship,
                            "is_hit": board.is_hit
                        }
                        for board in player1_boards
                    ],
                    "player2": [
                        {
                            "x": board.x,
                            "y": board.y,
                            "is_ship": board.is_ship,
                            "is_hit": board.is_hit
                        }
                        for board in player2_boards
                    ]
                }
            }
            result.append(game_data)

        return result