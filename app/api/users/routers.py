from fastapi import APIRouter, Request, Form, HTTPException, status , UploadFile , File
from fastapi.responses import RedirectResponse
import os
from uuid import uuid4
from app.core.config import templates
from app.api.users.crud import get_user, create_user , update_user


router = APIRouter(tags=["users"])


@router.get("/register/")
async def register_user(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@router.post("/register/")
async def register_page(request: Request,username: str = Form(...), password: str = Form(...), confirmPassword: str = Form(...)):
    from app.auth import hash_password
    if not username or not password or not confirmPassword:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing data")
    error = None

    if not username or not password or not confirmPassword:
        error = "Заполните все поля."
    elif get_user(username=username):
        error = "Пользователь с таким именем уже зарегистрирован."
    elif password != confirmPassword:
        error = "Пароли не совпадают."

    if error:
        return templates.TemplateResponse(
            "register.html",
            {"error": error, "username": username, "request": request,}
        )

    hashed = hash_password(password)
    create_user(
        username=username,
        password=hashed,
        photo="https://upload.wikimedia.org/wikipedia/commons/2/20/Photoshop_CC_icon.png"
    )
    return RedirectResponse(url="/login/", status_code=303)


@router.get("/login/")
async def login_user(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/login/")
async def login_page(request: Request, username: str = Form(...), password: str = Form(...)):
    from app.auth import verify_password, create_access_token

    error = None

    # Проверка на пустые поля
    if not username or not password:
        error = "Заполните все поля."
    else:
        try:
            user = dict(get_user(username=username))
        except Exception:
            user = None

        if not user:
            error = "Пользователь с таким именем не найден."
        elif not verify_password(password, user.get("password")):
            error = "Неверный пароль."

    if error:
        return templates.TemplateResponse(
            "login.html",
            {"error": error, "username": username, "request": request}
        )

    access_token = create_access_token(data={"sub": username})
    response = RedirectResponse(url='/', status_code=303)
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        samesite="lax",
        secure=False,
        max_age=60 * 60 * 24 * 7,
        path="/",
    )
    return response


@router.get('/profile/')
async def profile(request: Request):
    from app.auth import get_current_user
    try:
        current_user = get_current_user(request)
        if not current_user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

    return templates.TemplateResponse("profile.html", {"request": request, "user": current_user})


@router.get('/profile/edit/')
async def profile_edit(request: Request):
    from app.auth import get_current_user
    try:
        current_user = get_current_user(request)
        if not current_user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

    return templates.TemplateResponse("profile_edit.html", {"request": request, "user": current_user})

@router.post('/profile/edit/')
async def profile_edit_page(
    request: Request,
    username_new: str = Form(...),
    avatar: UploadFile = File(None)
):
    from app.auth import get_current_user , create_access_token
    try:
        current_user = get_current_user(request)
        if not current_user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

    try:
        existing_user = dict(get_user(username=username_new))
        if existing_user and existing_user.get("id") != current_user.get("id"):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User with this username already exists"
            )
    except Exception as e:
        pass

    photo_path = current_user.get("photo")


    if avatar.filename:
        allowed_types = ["image/jpeg", "image/png"]

        if avatar.content_type not in allowed_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid file type. Only JPEG, PNG are allowed."
            )

        if photo_path and not photo_path.endswith("default.png"):
            old_path = os.path.join("app", "front", photo_path.lstrip("/"))
            if os.path.exists(old_path):
                try:
                    os.remove(old_path)
                except Exception:
                    pass

        file_ext = os.path.splitext(avatar.filename)[1]
        filename = f"{uuid4().hex}{file_ext}"
        file_path = os.path.join('app', 'front', "avatars", filename)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        content = await avatar.read()
        with open(file_path, "wb") as f:
            f.write(content)

        photo_path = f"/avatars/{filename}"

    update_user(
        user_id=current_user.get("id"),
        username_new=username_new,
        photo_new=photo_path
    )

    access_token = create_access_token(data={"sub": username_new})
    response = RedirectResponse(url='/', status_code=303)
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        samesite="lax",
        secure=False,
        max_age=60*60*24*7,
        path="/",
    )
    return response


@router.get("/get-token")
def get_token(request: Request ):
    from app.auth import get_current_user
    try:
        current_user = get_current_user(request)
        if not current_user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

    token = request.cookies.get("access_token")
    return {"token": token}


@router.get("/logout/")
async def logout():
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie("access_token", path="/")
    return response