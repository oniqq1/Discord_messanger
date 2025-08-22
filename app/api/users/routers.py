from fastapi import HTTPException, status, APIRouter , Depends
from app.api.users.crud import get_user,create_user
from .schemas import UserCreate
from app.auth import hash_password , verify_password , create_access_token , Token
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter(tags=["users"])


@router.post("/register/")
async def register_user(data:UserCreate = Depends()):

    if not data:
       return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    if get_user(username=data.username):
        return HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="User already registered"
        )

    hashed_password = hash_password(data.password)

    user = create_user(username=data.username,password=hashed_password,photo=data.photo)

    return user


@router.post("/login")
async def login_user(data: OAuth2PasswordRequestForm = Depends()):

    if not data:
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    user = dict(get_user(username=data.username))

    if not user:
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    if not verify_password(data.password, user.get('password')):
        print(verify_password(data.password, user.get('password')))
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect password"
        )

    token = create_access_token(data={"sub": user.get('username')})

    return Token(access_token=token)