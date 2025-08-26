from fastapi import WebSocket, status, Request, WebSocketDisconnect, APIRouter, Depends, HTTPException
from app.core.config import templates
from app.auth import get_current_user
from jose import jwt, JWTError
from app.core.config import settings
from app.api.users.crud import get_user
from app.core.database import add_room , add_member_to_room , add_message
router = APIRouter()
connections = {}

@router.get("/")
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@router.get("/about/")
async def about(request: Request):
    return templates.TemplateResponse("about.html", {"request": request})

@router.get("/chat/")
async def get_chat(request: Request, current_user: dict = Depends(get_current_user)):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")


    current_user["photo"].replace("\\", "//")
    return templates.TemplateResponse("chat.html", {"request": request, "user": current_user })

@router.websocket("/ws/{room}")
async def websocket_endpoint(websocket: WebSocket, room: str):
    token = websocket.cookies.get("access_token")
    if not token:
        await websocket.close(code=1008)
        return
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
    connections.setdefault(room, []).append(websocket)

    user_id = get_current_user(token=token).get("id")
    add_room(room,user_id)
    add_member_to_room(room,user_id)

    try:
        while True:
            data = await websocket.receive_text()
            add_message(user_id, room, data)
            for client in list(connections.get(room, [])):
                await client.send_text(f"{data}")
    except WebSocketDisconnect:
        connections[room].remove(websocket)
        if not connections[room]:
            del connections[room]