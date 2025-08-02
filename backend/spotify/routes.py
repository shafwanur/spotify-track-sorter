import os
from dotenv import load_dotenv

from fastapi import APIRouter, Header

from spotify.models import AccessTokenRequest
from spotify.helpers import (
    get_cached_access_token,
    create_access_token,
    create_spotify_user_id,
)

load_dotenv()

BACKEND_ENDPOINT = os.getenv("BACKEND_ENDPOINT")
SPOTIFY_ENDPOINT = "https://accounts.spotify.com"

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = f"{BACKEND_ENDPOINT}/spotify/success"

router = APIRouter(prefix="/spotify", tags=["spotify"])


@router.post("/token/access") # will be called very often
def retrieve_access_token(payload: AccessTokenRequest):
    # Try retrieving from cache, otherwise create it 
    access_token = get_cached_access_token(spotify_user_id=payload.spotify_user_id)
    if access_token is None:  # if it doesn't exist, create a new one
        access_token = create_access_token(payload)

    return {"access_token": access_token}


@router.get("/me")
def get_me(access_token: str = Header(...)):
    '''
    Given access_token, return spotify_user_id. 
    Will probably never be called, but keeping an endpoint. 
    '''
    spotify_user_id = create_spotify_user_id(access_token=access_token)
    return {"spotify_user_id": spotify_user_id}
