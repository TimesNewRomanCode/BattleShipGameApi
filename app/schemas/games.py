import uuid
from datetime import datetime

from pydantic import BaseModel, Field
from typing import Optional, List


class CreateGameRequest(BaseModel):
    player1_sid: uuid.UUID
    player2_sid: uuid.UUID


class CreateGameResponse(BaseModel):
    game_sid: uuid.UUID
    status: str
    player1_sid: uuid.UUID
    player2_sid: uuid.UUID
    message: str


class BoardCellResponse(BaseModel):
    x: int
    y: int
    is_ship: bool
    is_hit: bool


class GameBoardsResponse(BaseModel):
    player1: List[BoardCellResponse]
    player2: List[BoardCellResponse]


class ActiveGameResponse(BaseModel):
    game_sid: uuid.UUID
    status: str
    player1_sid: uuid.UUID
    player2_sid: uuid.UUID
    current_turn_sid: Optional[uuid.UUID]
    boards: GameBoardsResponse
