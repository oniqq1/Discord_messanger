from fastapi import APIRouter, Request

from app.core.config import templates


router = APIRouter()


@router.get("/register/")
async def register_user(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@router.get("/login/")
async def login_user(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})