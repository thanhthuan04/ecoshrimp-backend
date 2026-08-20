import json

from fastapi import WebSocket

class WebSocketManager:
    def __init__(self) -> None:
        self._connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self._connections.append(websocket)
        print(f"[WS] Client kết nối. Tổng: {len(self._connections)}")

    def disconnect(self, websocket: WebSocket) -> None:
        if websocket in self._connections:
            self._connections.remove(websocket)
        print(f"[WS] Client ngắt kết nối. Tổng: {len(self._connections)}")

    async def broadcast(self, data: dict) -> None:
        message = json.dumps(data, default=str)
        dead_connections: list[WebSocket] = []

        for connection in self._connections:
            try:
                await connection.send_text(message)
            except Exception:
                dead_connections.append(connection)

        for connection in dead_connections:
            self.disconnect(connection)

ws_manager = WebSocketManager()