from pydantic import BaseModel


class User(BaseModel):
    id: int | None = None
    name: str
    email: str


class UserIn(User):
    password: str
