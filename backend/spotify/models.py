from pydantic import BaseModel

class AccessTokenRequest(BaseModel):
    spotify_user_id: str
    refresh_token: str
