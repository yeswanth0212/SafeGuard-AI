from pydantic import BaseModel

class UserCreate(BaseModel):
    username: str
    password: str
    full_name: str
    age: int
    role: str
    profile_photo: str = None

class Login(BaseModel):
    username: str
    password: str
