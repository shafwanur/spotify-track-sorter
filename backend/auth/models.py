from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str

class User(BaseModel):
    spotify_user_id: str | None = None