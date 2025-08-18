from fastapi import FastAPI

from .core.database import create_tables
from app.api import user_router
from app.tests import test_router


app = FastAPI(
    title="My API",
    description="Example project",
    version="0.1.0",
		on_startup=[create_tables],
)
app.include_router(user_router)
app.include_router(test_router)