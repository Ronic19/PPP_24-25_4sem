from fastapi import WebSocket
from typing import Dict, List

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}


    async def connect(self, user_email: str, websocket: WebSocket):
        await websocket.accept()
        if user_email not in self.active_connections:
            self.active_connections[user_email] = []
        self.active_connections[user_email].append(websocket)
        

    def disconnect(self, user_email: str, websocket: WebSocket):
        if user_email in self.active_connections:
            self.active_connections[user_email].remove(websocket)
            if not self.active_connections[user_email]:
                del self.active_connections[user_email]


    async def send_message(self, user_email: str, message: dict):
        if user_email in self.active_connections:
            for con in self.active_connections.get(user_email):
                await con.send_json(message)


manager = ConnectionManager()

