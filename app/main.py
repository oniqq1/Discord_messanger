import uvicorn

from fastapi import FastAPI
from app.core.config import app


if __name__ == "__main__":
		uvicorn.run(app, port=8080)