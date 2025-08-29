from fastapi import WebSocket, status, Request, WebSocketDisconnect, APIRouter, Depends, HTTPException
from app.core.config import templates
from app.auth import get_current_user
from jose import jwt, JWTError
from app.core.config import settings
from app.api.users.crud import get_user, get_user_by_id
from app.core.database import add_room , add_member_to_room , add_message , if_exists_room , get_messages_by_room
import datetime
router = APIRouter()
connections = {}

@router.get("/")
async def index(request: Request ):
    token = request.cookies.get("access_token")
    if token:
        user = dict(get_current_user(token=token))
        return templates.TemplateResponse("index.html", {"request": request , "is_authenticated": token , 'user': user})
    return templates.TemplateResponse("index.html", {"request": request , "is_authenticated": token})

@router.get("/about/")
async def about(request: Request):
    token = request.cookies.get("access_token")
    if token:
        user = dict(get_current_user(token=token))
        return templates.TemplateResponse("about.html", {"request": request , "is_authenticated": token , 'user': user})
    return templates.TemplateResponse("about.html", {"request": request})

@router.get("/chat/")
async def get_chat(request: Request, current_user: dict = Depends(get_current_user)):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")


    current_user["photo"].replace("\\", "//")
    return templates.TemplateResponse("chat.html", {"request": request, "user": current_user , "is_authenticated": token})

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

    user = get_current_user(token=token)
    user_id = user.get("id")

    if not if_exists_room(room):
        add_room(room,user_id)
        add_member_to_room(room,user_id)
    else:
        messages = get_messages_by_room(room)
        for msg in messages:
            author = get_user_by_id(msg["sender_id"])
            await websocket.send_json({
                "sender_id": msg["sender_id"],
                "username": author["username"],
                "photo": author["photo"].replace("\\", "//"),
                "content": msg["content"],
                "timestamp": msg["timestamp"]
            })

    try:
        while True:
            data = await websocket.receive_text()
            add_message(user_id, room, data)
            for client in list(connections.get(room, [])):
                try:
                    await client.send_json({
                        "sender_id": user_id,
                        "username": user["username"],
                        "photo": user["photo"].replace("\\", "//"),
                        "content": data,
                        "timestamp": f"{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}"
                    })
                except RuntimeError:
                    connections[room].remove(client)

    except WebSocketDisconnect:
        try:
            connections[room].remove(websocket)
            if not connections[room]:
                del connections[room]
        except KeyError:
            pass

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