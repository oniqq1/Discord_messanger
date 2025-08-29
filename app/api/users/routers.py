import os

from fastapi import APIRouter, Request, Form, HTTPException, status , UploadFile , File
from fastapi.responses import RedirectResponse
from uuid import uuid4

from app.core.config import templates, logger
from app.api.users.crud import get_user, create_user , update_user
from app.core.database import get_messages_all , get_rooms_where_user

router = APIRouter(tags=["users"])


@router.get("/register/")
async def register_user(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@router.post("/register/")
async def register_page(request: Request,username: str = Form(...), password: str = Form(...), confirmPassword: str = Form(...)):
    from app.auth import hash_password
    if not username or not password or not confirmPassword:
        logger.info("Missing data")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing data")
    error = None

    if not username or not password or not confirmPassword:
        logger.info("Заповніть всі поля")
        error = "Заповніть всі поля"
    elif get_user(username=username):
        logger.info("Користувач з таким ім'ям вже існує: %s", username)
        error = "Користувач з таким ім'ям вже існує."
    elif password != confirmPassword:
        logger.info("Паролі не співпадають: %s != %s", password)
        error = "Паролі не співпадають"

    if error:
        logger.info("Успішно зареєстровано користувача: %s", username)
        return templates.TemplateResponse(
            "register.html",
            {"error": error, "username": username, "request": request,}
        )

    hashed = hash_password(password)
    create_user(
        username=username,
        password=hashed,
        photo="https://i.pinimg.com/736x/7d/ad/d4/7dadd43f4b9faa58bf53ab29d734aa8b.jpg"
    )
    return RedirectResponse(url="/login/", status_code=303)


@router.get("/login/")
async def login_user(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/login/")
async def login_page(request: Request, username: str = Form(...), password: str = Form(...)):
    from app.auth import verify_password, create_access_token

    error = None

    if not username or not password:
        logger.info("Заповніть всі поля")
        error = "Заповніть всі поля"
    else:
        try:
            user = dict(get_user(username=username))
        except Exception:
            user = None

        if not user:
            logger.info("Користувача з таким ім'ям не існує: %s", username)
            error = "Користувача з таким ім'ям не існує"
        elif not verify_password(password, user.get("password")):
            logger.info("Невірний пароль для користувача: %s", username)
            error = "Невірний пароль"

    if error:
        logger.info("Успішно увійшов користувач: %s", username)
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


@router.get("/profile/")
async def profile(request: Request):
    from app.auth import get_current_user
    try:
        current_user = dict(get_current_user(request))
        if not current_user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

    id = current_user.get('id')
    print(id)

    return templates.TemplateResponse("profile.html", {"request": request, "user": current_user , "messages_count": len(get_messages_all(id)) , "rooms_count": get_rooms_where_user(id) , "is_authenticated":current_user, "messages":get_messages_all(id)})


@router.get("/profile/edit/")
async def profile_edit(request: Request):
    from app.auth import get_current_user
    try:
        current_user = get_current_user(request)
        if not current_user:
            logger.info("Не авторизований")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Не авторизований")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

    return templates.TemplateResponse("profile_edit.html", {"request": request, "user": current_user , "is_authenticated": True })


@router.post("/profile/edit/")
async def profile_edit_page(
    request: Request,
    username_new: str = Form(...),
    avatar: UploadFile = File(None)
):
    from app.auth import get_current_user , create_access_token
    try:
        current_user = get_current_user(request)
        if not current_user:
            logger.info("Спроба редагування профілю без автентифікації")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Не авторизований")
        logger.info(f"Користувач {current_user.get('username')} намагається оновити свій профіль")
    except Exception as e:
        logger.error(f"Помилка автентифікації: {e}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

    try:
        existing_user = dict(get_user(username=username_new))
        if existing_user and existing_user.get("id") != current_user.get("id"):
            logger.info(f"Конфлікт імен користувачів: {username_new} вже існує")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Користувач з таким ім'ям вже існує."
            )
    except Exception as e:
        logger.error(f"Помилка перевірки існуючого імені користувача: {e}")
        pass

    photo_path = current_user.get("photo")

    if avatar.filename:
        allowed_types = ["image/jpeg", "image/png"]

        if avatar.content_type not in allowed_types:
            logger.warning(f"Користувач {current_user.get('username')} завантажено недійсний тип файлу: {avatar.content_type}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Невірний формат файлу. Дозволені формати: jpg, png."
            )

        if photo_path and not photo_path.endswith("default.png"):
            old_path = os.path.join("app", "front", photo_path.lstrip("/"))
            if os.path.exists(old_path):
                try:
                    os.remove(old_path)
                    logger.info(f"Видалено старий аватар: {old_path}")
                except Exception as e:
                    logger.error(f"Не вдалося видалити старий аватар: {e}")

        file_ext = os.path.splitext(avatar.filename)[1]
        filename = f"{uuid4().hex}{file_ext}"
        file_path = os.path.join('app', 'front', "avatars", filename)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        content = await avatar.read()
        with open(file_path, "wb") as f:
            f.write(content)
        logger.info(f"Збережено новий аватар для користувача {current_user.get('username')} в {file_path}")
        photo_path = f"/avatars/{filename}"

    update_user(
        user_id=current_user.get("id"),
        username_new=username_new,
        photo_new=photo_path
    )
    logger.info(f"Профіль користувача оновлено {current_user.get('username')} з новим іменем користувача: {username_new}")

    access_token = create_access_token(data={"sub": username_new})
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
    logger.info(f"Встановити новий cookie токена доступу для користувача {username_new}")
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
    logger.info("Успішно вийшов користувач")
    return response