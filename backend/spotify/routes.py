# Standard library imports
import os
import requests
from urllib.parse import urlencode

# FastAPI imports
from fastapi import APIRouter, HTTPException, Header, Request
from fastapi.responses import RedirectResponse, JSONResponse

# Third-party library imports 
from sqlalchemy import text
from dotenv import load_dotenv

# Local imports
from spotify.helpers import create_refresh_token, store_refresh_token, get_refresh_token, get_cached_access_token, create_access_token, generate_random_string, get_scopes, create_spotify_user_id, get_spotify_user_id, store_spotify_user_id
from spotify.models import RefreshTokenRequest, AccessTokenRequest

# Global & Environment Variables
load_dotenv()

BACKEND_ENDPOINT = os.getenv("BACKEND_ENDPOINT")
SPOTIFY_ENDPOINT = os.getenv("SPOTIFY_ENDPOINT")

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = f"{BACKEND_ENDPOINT}/spotify/success" 

router = APIRouter(prefix="/spotify", tags=["spotify"])


@router.get("/login") # TODO: should probably be a post request, but FastAPI doesn't care, and I'm ignoring it for now. 
def login():
    state = generate_random_string(16)
    scope = get_scopes()
    query_params = {
        "response_type": "code",
        "client_id": CLIENT_ID,
        "scope": scope,
        "redirect_uri": REDIRECT_URI,
        "state": state,
    }
    auth_url = f"{SPOTIFY_ENDPOINT}/authorize?" + urlencode(query_params)
    return RedirectResponse(auth_url)

@router.get("/success") 
def auth_callback(request: Request):
    state = request.query_params.get("state")
    auth_code = request.query_params.get("code")

    if not auth_code:
        return JSONResponse({"error": "No auth_code returned"}, status_code=400)

    return JSONResponse({ # TODO: would making a call to /spotify/login return this json? 
        "message": "Authorization successful",
        "code": auth_code,
        "state": state
    })

@router.post("/token/refresh") # expects the auth_code to generate refresh_token. or if it exists (in memory in the dict), just returns it. refresh_tokens are permanent.
def retrieve_refresh_token(payload: RefreshTokenRequest): # TODO: should probably be async functions ... will change later. 
    if payload.auth_code: # if auth_code passed, generate new refresh_token, store in db 
        refresh_token = create_refresh_token(auth_code=payload.auth_code)
        store_refresh_token(user_id=payload.user_id, refresh_token=refresh_token)

    # Get refresh_token from the db using user_id
    refresh_token = get_refresh_token(user_id=payload.user_id)
        
    return {"refresh_token": refresh_token} # TODO: proper json to return? 

@router.post("/token/access")
def retrieve_access_token(payload: AccessTokenRequest):
    # Try retrieving from cache
    access_token = get_cached_access_token(user_id=payload.user_id)
    if not access_token: # if it doesn't exist, create a new one
        access_token = create_access_token(user_id=payload.user_id)
    
    return {"access_token": access_token}

@router.get("/me")
def get_me(user_id: str, access_token: str = Header(...)):
    spotify_user_id = get_spotify_user_id(user_id=user_id)
    if spotify_user_id is None: 
        spotify_user_id = create_spotify_user_id(access_token=access_token)
        
    store_spotify_user_id(user_id=user_id, spotify_user_id=spotify_user_id)
    return {"spotify_user_id": spotify_user_id, "user_id": user_id}