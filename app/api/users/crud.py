from fastapi import HTTPException, status, APIRouter

from .models import User
from app.core.database import create_user, get_user


router = APIRouter(prefix="/users", tags=["users"])


@router.post("/register/")
async def register_user(data:User):
    if not data:
       return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    if get_user(username=data.username):
        return HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="User already registered"
        )
    user = create_user(username=data.username,email=data.email,password=data.password,photo=data.photo)
    return user