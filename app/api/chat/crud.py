from fastapi import WebSocket, status, Request, WebSocketDisconnect, APIRouter
from app.core.config import templates


router = APIRouter()


@router.get(
    "/chat/",
    summary="Сторінка WebSocket чату",
    description="Повертає HTML-сторінку з WebSocket чатом.",
    tags=["Чат"],
    status_code=status.HTTP_200_OK,
)
async def get_chat(request: Request):
    return templates.TemplateResponse("chat.html", {"request": request})


connections = {}

@router.websocket("/ws/{room}")
async def websocket_endpoint(websocket: WebSocket, room: str):
    await websocket.accept()

    if room not in connections:
        connections[room] = []

    connections[room].append(websocket)

    try:
        while True:
            data = await websocket.receive_text()

            for client in connections[room]:
                await client.send_text(data)

    except WebSocketDisconnect:
        connections[room].remove(websocket)
        if not connections[room]:
            del connections[room]