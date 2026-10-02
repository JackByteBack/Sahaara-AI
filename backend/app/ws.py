"""WebSocket connection registry — broadcasts analysis events to live consoles."""
from __future__ import annotations

import asyncio
import logging

from fastapi import WebSocket

log = logging.getLogger("sahaara.ws")


class ConnectionManager:
    def __init__(self) -> None:
        self._rooms: dict[str, set[WebSocket]] = {}
        self._lock = asyncio.Lock()

    async def connect(self, case_id: str, ws: WebSocket) -> None:
        await ws.accept()
        async with self._lock:
            self._rooms.setdefault(case_id, set()).add(ws)

    async def disconnect(self, case_id: str, ws: WebSocket) -> None:
        async with self._lock:
            room = self._rooms.get(case_id)
            if room:
                room.discard(ws)
                if not room:
                    self._rooms.pop(case_id, None)

    async def broadcast(self, case_id: str, message: dict) -> None:
        room = self._rooms.get(case_id)
        if not room:
            return
        dead = []
        for ws in list(room):
            try:
                await ws.send_json(message)
            except Exception:
                dead.append(ws)
        for ws in dead:
            await self.disconnect(case_id, ws)


manager = ConnectionManager()


def broadcast_sync(case_id: str, message: dict) -> None:
    """Fire-and-forget broadcast from sync (threadpool) contexts."""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        return
    loop.create_task(manager.broadcast(case_id, message))
