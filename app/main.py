from fastapi import Depends,FastAPI
import uvicorn
from .auth import oauth2_scheme
from .api.users import router as users_router
from .core.database import create_tables


app = FastAPI(on_startup=(create_tables,))


# routers = [users_router]
#
# for r in routers:
#     app.include_router(r, prefix="/api")


@app.get("/test/")
async def test_endpoint(token: str = Depends(oauth2_scheme)):
    return {"message": "Hello, World!"}

if __name__ == "__main__":
    app.include_router(users_router, prefix="/api")
    uvicorn.run("app.main:app", port=8080, reload=True)