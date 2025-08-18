from fastapi import Depends
from fastapi import APIRouter

from app.auth import oauth2_scheme


router = APIRouter(prefix="/test", tags=["test"])


@router.get("/test/")
async def test_endpoint(token: str = Depends(oauth2_scheme)):
    return {"message": "Hello, World!"}