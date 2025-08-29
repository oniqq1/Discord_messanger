from fastapi import Depends, APIRouter
from app.auth import get_current_user


router = APIRouter( tags=["test"])


@router.get("/test/")
async def test_endpoint(current_user: dict = Depends(get_current_user)):
    return {
        "message": "pong",
        "user": current_user.get("username") if current_user else None
    }