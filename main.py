import uvicorn

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.core.database import create_tables
from app.api.users import user_router
from app.tests import test_router
from app.api.chat import chat_router


app = FastAPI(
    title="My API",
    description="Example project",
    version="0.1.0",
		on_startup=[create_tables],
)

app.mount("/static", StaticFiles(directory="app/front/static"), name="static")
app.mount("/avatars", StaticFiles(directory="app/front/avatars"), name="avatars")


app.include_router(user_router)
app.include_router(test_router)
app.include_router(chat_router)


if __name__ == "__main__":
    uvicorn.run("main:app", port=8000, reload=True)