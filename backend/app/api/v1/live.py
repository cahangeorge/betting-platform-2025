import asyncio
import json
from typing import Any

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.database import async_session_factory
from app.models import Match, OddsEntry, PredictionRun, ModelPrediction

router = APIRouter(prefix="/live", tags=["live"])

# Connection manager for active WebSocket clients
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        async with self._lock:
            self.active_connections.append(websocket)

    async def disconnect(self, websocket: WebSocket):
        async with self._lock:
            if websocket in self.active_connections:
                self.active_connections.remove(websocket)

    async def broadcast(self, message: dict[str, Any]):
        disconnected = []
        async with self._lock:
            connections = list(self.active_connections)
        for conn in connections:
            try:
                await conn.send_text(json.dumps(message))
            except Exception:
                disconnected.append(conn)
        async with self._lock:
            for d in disconnected:
                if d in self.active_connections:
                    self.active_connections.remove(d)


manager = ConnectionManager()


@router.websocket("/ws")
async def live_websocket(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive and listen for client messages
            data = await websocket.receive_text()
            try:
                msg = json.loads(data)
                action = msg.get("action")
                if action == "subscribe":
                    channel = msg.get("channel", "all")
                    await websocket.send_text(json.dumps({"type": "subscribed", "channel": channel}))
                elif action == "ping":
                    await websocket.send_text(json.dumps({"type": "pong"}))
                else:
                    await websocket.send_text(json.dumps({"type": "error", "message": f"Unknown action: {action}"}))
            except json.JSONDecodeError:
                await websocket.send_text(json.dumps({"type": "error", "message": "Invalid JSON"}))
    except WebSocketDisconnect:
        await manager.disconnect(websocket)


async def broadcast_odds_update(match_id: int, odds: dict[str, Any]):
    """Broadcast odds update to all connected clients."""
    await manager.broadcast({
        "type": "odds_update",
        "match_id": match_id,
        "data": odds,
        "timestamp": asyncio.get_event_loop().time(),
    })


async def broadcast_prediction_update(run_id: int, status: str, progress: float | None = None):
    """Broadcast prediction run status update."""
    await manager.broadcast({
        "type": "prediction_update",
        "run_id": run_id,
        "status": status,
        "progress": progress,
        "timestamp": asyncio.get_event_loop().time(),
    })


async def broadcast_match_update(match_id: int, event: str, data: dict[str, Any]):
    """Broadcast match event (goal, card, substitution, etc.)."""
    await manager.broadcast({
        "type": "match_event",
        "match_id": match_id,
        "event": event,
        "data": data,
        "timestamp": asyncio.get_event_loop().time(),
    })
