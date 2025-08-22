from pydantic import BaseModel


class UserCreate(BaseModel):
    username: str
    password: str
    email: str
    photo: str


class User(BaseModel):
    username: str
    password: str
    email: str
