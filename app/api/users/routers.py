
from fastapi import APIRouter, Request, Form, HTTPException, status
from fastapi.responses import RedirectResponse
from app.core.config import templates
from app.api.users.crud import get_user, create_user


router = APIRouter(tags=["users"])




@router.get("/register/")
async def register_user(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@router.post("/register/")
async def register_page(username: str = Form(...), password: str = Form(...), confirmPassword: str = Form(...)):
    from app.auth import hash_password, verify_password, create_access_token
    if not username or not password or not confirmPassword:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing data")

    if get_user(username=username):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already registered")

    if password != confirmPassword:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Passwords do not match")

    hashed = hash_password(password)
    create_user(username=username, password=hashed, photo="https://upload.wikimedia.org/wikipedia/commons/2/20/Photoshop_CC_icon.png")
    return RedirectResponse(url="/login/", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/login/")
async def login_user(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/login/")
async def login_page(username: str = Form(...), password: str = Form(...)):
    from app.auth import hash_password, verify_password, create_access_token
    user = dict(get_user(username))
    if not user or not verify_password(password, user.get("password")):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect credentials")

    access_token = create_access_token(data={"sub": username})
    redirect_url = f"/chat/?token={access_token}"
    return RedirectResponse(url=redirect_url, status_code=303)
