from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.websocket.manager import manager
from app.services.websocket import WebSocketService
from app.core.database import get_session
import uuid

router = APIRouter(prefix="/WS", tags=["WS"])
websocket_service = WebSocketService()


@router.websocket("/games/{game_sid}/play")
async def websocket_endpoint(websocket: WebSocket, game_sid: uuid.UUID):
    await websocket.accept()
    await manager.connect(game_sid, websocket)

    try:
        while True:
            data = await websocket.receive_json()
            action = data.get("action")

            async for session in get_session():
                if action == "start_game":
                    await handle_start_game(game_sid, session, websocket)
                elif action == "shoot":
                    await handle_shoot(game_sid, data, session, websocket)
                elif action == "surrender":
                    await handle_surrender(game_sid, data, session, websocket)
                else:
                    await websocket.send_json({"error": "Unknown action"})

    except WebSocketDisconnect:
        manager.disconnect(game_sid, websocket)
    except Exception as e:
        await websocket.send_json({"error": str(e)})
        manager.disconnect(game_sid, websocket)


async def handle_start_game(game_sid: uuid.UUID, session, websocket):
    success = await websocket_service.start_game(game_sid, session)
    if success:
        game = await websocket_service.games_crud.get_game_by_sid(game_sid, session)
        await manager.broadcast(
            game_sid,
            {"type": "game_started", "current_turn": str(game.current_turn_sid)},
        )
    else:
        await websocket.send_json({"error": "Cannot start game"})


async def handle_shoot(game_sid: uuid.UUID, data: dict, session, websocket):
    player_sid = uuid.UUID(data.get("player_sid"))
    x = data.get("x")
    y = data.get("y")

    if x is None or y is None:
        await websocket.send_json({"error": "Missing x or y coordinates"})
        return

    result = await websocket_service.handle_shot(game_sid, player_sid, x, y, session)

    if "error" in result:
        await websocket.send_json({"error": result["error"]})
        return

    await manager.broadcast(
        game_sid,
        {
            "type": "shot_result",
            "player_sid": str(player_sid),
            "x": x,
            "y": y,
            "result": result["result"],
            "next_turn": str(result["next_turn"]) if result.get("next_turn") else None,
            "game_over": result.get("game_over", False),
            "winner": str(result["winner"]) if result.get("winner") else None,
        },
    )


async def handle_surrender(game_sid: uuid.UUID, data: dict, session, websocket):
    player_sid = uuid.UUID(data.get("player_sid"))
    winner_sid = await websocket_service.surrender_game(game_sid, player_sid, session)

    if winner_sid:
        await manager.broadcast(
            game_sid,
            {"type": "game_over", "reason": "surrender", "winner": str(winner_sid)},
        )
    else:
        await websocket.send_json({"error": "Cannot surrender"})
