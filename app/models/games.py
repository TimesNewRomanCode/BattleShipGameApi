import enum
from typing import Optional
from uuid import UUID

from sqlalchemy import String, DateTime, Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from .base import Base


class GameStatus(enum.Enum):
    waiting = "created"
    active = "active"
    finished = "finished"


class Games(Base):
    __tablename__ = "games"

    player1_sid: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("players.sid"), nullable=False
    )
    player2_sid: Mapped[Optional[UUID]] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("players.sid"), nullable=True
    )
    status: Mapped[GameStatus] = mapped_column(
        Enum(GameStatus), default=GameStatus.waiting, nullable=False
    )
    winner_sid: Mapped[Optional[UUID]] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("players.sid"), nullable=True
    )
    current_turn_sid: Mapped[Optional[UUID]] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("players.sid"), nullable=True
    )
