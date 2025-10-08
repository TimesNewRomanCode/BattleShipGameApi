from sqlalchemy import UUID, Boolean, Integer
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base


class Boards(Base):
    __tablename__ = "boards"

    game_sid: Mapped[UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    player_sid: Mapped[UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    x: Mapped[int] = mapped_column(Integer, nullable=False)
    y: Mapped[int] = mapped_column(Integer, nullable=False)
    is_ship: Mapped[bool] = mapped_column(Boolean, default=False)
    is_hit: Mapped[bool] = mapped_column(Boolean, default=False)
