from fastapi import WebSocket
class WSConnectionManager:
    def __init__(self) -> None:
        self.connections:dict[str,WebSocket]  = {}
 
    async def connect(self, client_id: str, websocket: WebSocket):
        await websocket.accept()
        self.connections[client_id] = websocket

    async def disconnect(self, client_id):
        websocket: WebSocket = self.connections[client_id]
        await websocket.close()
        del self.connections[client_id]

    async def send_messages(self, client_id, message):
        websocket: WebSocket = self.connections[client_id]
        print('websocket',websocket,client_id)
        # await websocket.send_text('1111')
        await websocket.send_json(message)