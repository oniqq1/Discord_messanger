from fastapi import APIRouter

from .routers import router as user_router
from .models import *
from .schemas import *


router = APIRouter()
router.include_router(user_router)