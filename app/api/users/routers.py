from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse
from app.core.config import templates
from app.api.users.crud import get_user, create_user

router = APIRouter(tags=["users"])


@router.get("/register/")
async def register_user(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@router.post("/register/")
async def register_page(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    confirmPassword: str = Form(...)
):
    from app.auth import hash_password

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
            {"request": request, "error": error, "username": username}
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

    user = get_user(username)
    error = None

    if not user or not verify_password(password, user["password"]):
        error = "Неверное имя пользователя или пароль."

    if error:
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": error, "username": username}
        )

    access_token = create_access_token(data={"sub": username})
    redirect_url = f"/chat/?token={access_token}"
    return RedirectResponse(url=redirect_url, status_code=303)