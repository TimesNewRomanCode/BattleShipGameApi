from typing import Dict, List
import uuid

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[uuid.UUID, List] = {}

    async def connect(self, game_sid: uuid.UUID, websocket):
        if game_sid not in self.active_connections:
            self.active_connections[game_sid] = []
        self.active_connections[game_sid].append(websocket)

    def disconnect(self, game_sid: uuid.UUID, websocket):
        if game_sid in self.active_connections:
            self.active_connections[game_sid].remove(websocket)
            if not self.active_connections[game_sid]:
                del self.active_connections[game_sid]

    async def send_personal_message(self, message: dict, websocket):
        await websocket.send_json(message)

    async def broadcast(self, game_sid: uuid.UUID, message: dict):
        if game_sid in self.active_connections:
            for connection in self.active_connections[game_sid]:
                await connection.send_json(message)

manager = ConnectionManager()