from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.services.board_events import manager

router = APIRouter()


@router.websocket("/ws/board")
async def board_websocket(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

