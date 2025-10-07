from sqlalchemy import Column, Integer, ForeignKey, Boolean, String, UUID
from .base import Base

class Boards(Base):
    __tablename__ = "boards"

    game_sid = Column(UUID(as_uuid=True), nullable=False)
    player_sid = Column(UUID(as_uuid=True), nullable=False)
    x = Column(Integer, nullable=False)
    y = Column(Integer, nullable=False)
    is_ship = Column(Boolean, default=False)
    is_hit = Column(Boolean, default=False)