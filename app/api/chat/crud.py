from fastapi import WebSocket, status, Request, WebSocketDisconnect, APIRouter , Depends
from app.core.config import templates
from app.auth import get_current_user
from jose import jwt, JWTError
from app.core.config import settings
router = APIRouter()
connections = {}


@router.get("/")
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@router.get("/about/")
async def about(request: Request):
    return templates.TemplateResponse("about.html", {"request": request})

# Страница чата
@router.get("/chat/")
async def get_chat(request: Request, current_user: dict = get_current_user):
    return templates.TemplateResponse("chat.html", {"request": request, "user": current_user})

# WebSocket
@router.websocket("/ws/{room}")
async def websocket_endpoint(websocket: WebSocket, room: str):
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=1008)
        return

    from jose import jwt, JWTError
    from app.core.config import settings
    from app.api.users.crud import get_user

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username = payload.get("sub")
        if not username or not get_user(username):
            await websocket.close(code=1008)
            return
    except JWTError:
        await websocket.close(code=1008)
        return

    await websocket.accept()
    if room not in connections:
        connections[room] = []
    connections[room].append(websocket)

    try:
        while True:
            data = await websocket.receive_text()
            for client in connections[room]:
                await client.send_text(f"{data}")
    except WebSocketDisconnect:
        connections[room].remove(websocket)
        if not connections[room]:
            del connections[room]