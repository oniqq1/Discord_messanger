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

@router.get("/my-rooms/")
async def my_rooms(current_user: dict = Depends(get_current_user)):
    from app.core.database import get_db_connection

    user_id = current_user["id"]
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT roomname, members FROM rooms")
        rows = cursor.fetchall()

    user_rooms = []
    for row in rows:
        members = row["members"].split(",")
        if str(user_id) in members:
            user_rooms.append(row["roomname"])

    return {"rooms": user_rooms}

@router.delete("/delete-room/{roomname}")
async def delete_room(roomname: str, current_user: dict = Depends(get_current_user)):
    from app.core.database import get_db_connection

    user_id = current_user["id"]
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT members FROM rooms WHERE roomname = ?", (roomname,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Комната не найдена")

        members = row["members"].split(",")
        if str(user_id) not in members:
            raise HTTPException(status_code=403, detail="Вы не участник этой комнаты")

        cursor.execute("DELETE FROM rooms WHERE roomname = ?", (roomname,))
        conn.commit()

    if roomname in connections:
        for ws in connections[roomname]:
            await ws.close(code=1000)
        del connections[roomname]

    return {"detail": "Комната удалена"}