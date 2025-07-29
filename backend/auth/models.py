from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class User(BaseModel):
    id: int | None = None
    username: str | None = None
    disabled: str | None = None


class UserInDB(User):
    hashed_password: str