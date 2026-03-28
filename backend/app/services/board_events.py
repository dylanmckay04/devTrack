from fastapi import WebSocket
from typing import Any


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict[str, Any]):
        disconnected: list[WebSocket] = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                disconnected.append(connection)

        for connection in disconnected:
            self.disconnect(connection)


manager = ConnectionManager()


async def broadcast_application_event(event_type: str, application: Any):
    await manager.broadcast(
        {
            "type": event_type,
            "application": {
                "id": application.id,
                "owner_id": application.owner_id,
                "company": application.company,
                "role": application.role,
                "status": application.status.value if hasattr(application.status, "value") else application.status,
                "job_url": application.job_url,
                "notes": application.notes,
                "applied_at": application.applied_at.isoformat() if application.applied_at else None,
                "created_at": application.created_at.isoformat() if application.created_at else None,
                "updated_at": application.updated_at.isoformat() if application.updated_at else None,
            },
        }
    )