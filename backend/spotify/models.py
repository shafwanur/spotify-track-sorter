from pydantic import BaseModel


class RefreshTokenRequest(BaseModel): # TODO: might be needed to be renamed to RefreshTokenRequest later, if its not generalisable 
    user_id: str
    auth_code: str | None = None # depending on what gets sent, return or create the refresh_token. TODO: is this a good design? 

class AccessTokenRequest(BaseModel):
    user_id: str 