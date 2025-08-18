from fastapi import Depends
from fastapi import APIRouter
from app.auth import oauth2_scheme , get_current_user


router = APIRouter(prefix="/test", tags=["test"])


@router.get("/test/")
async def test_endpoint(token: str = Depends(oauth2_scheme)):
    if get_current_user(token) is None:
        return {"message": "Unauthorized access"}
    return {"message": "Hello, World!"}