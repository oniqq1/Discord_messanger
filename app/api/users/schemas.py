from pydantic import BaseModel


class UserCreate(BaseModel):
    username: str
    password: str
    photo: str


class User(BaseModel):
    username: str
    password: str