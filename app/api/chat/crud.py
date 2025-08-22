from fastapi import WebSocket, status, Request, WebSocketDisconnect, APIRouter, Depends

from app.core.config import templates
from app.auth import oauth2_scheme


router = APIRouter()
connections = {}


@router.get("/")
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@router.get("/about/")
async def about(request: Request):
    return templates.TemplateResponse("about.html", {"request": request})

@router.get(
    "/chat/",
    summary="Сторінка WebSocket чату",
    description="Повертає HTML-сторінку з WebSocket чатом.",
    tags=["Чат"],
    status_code=status.HTTP_200_OK,
)
async def get_chat(request: Request, token: str = Depends(oauth2_scheme)):
    return templates.TemplateResponse("chat.html", {"request": request})

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