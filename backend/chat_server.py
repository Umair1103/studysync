import uuid
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware


PUBLIC_URL = "  http://localhost:8000"   # <-- PUT YOUR URL HERE

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# room_id -> set of WebSocket connections
rooms = {}


@app.get("/create_room")
def create_room():
    room_id = str(uuid.uuid4())[:8]
    rooms[room_id] = set()

    

    return {
        "room_id": room_id,
        
    }


@app.websocket("/ws/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str):
    await websocket.accept()

    if room_id not in rooms:
        rooms[room_id] = set()

    rooms[room_id].add(websocket)

    try:
        while True:
            message = await websocket.receive_text()

            disconnected_clients = []

            for client in rooms[room_id]:
                try:
                    await client.send_text(message)
                except:
                    disconnected_clients.append(client)

            # remove dead connections
            for client in disconnected_clients:
                rooms[room_id].remove(client)

    except WebSocketDisconnect:
        if websocket in rooms[room_id]:
            rooms[room_id].remove(websocket)