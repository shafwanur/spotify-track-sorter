import os
from urllib.parse import urlencode
from dotenv import load_dotenv

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi import Depends

from db.init import get_session
from auth.models import Token, User
from auth.helpers import (
    get_scopes,
    generate_random_string, 
    get_current_user,
    create_jwt_token,
    db_update,
)

from spotify.helpers import (
    create_spotify_user_id,
    create_refresh_token,
    create_access_token
)


load_dotenv()
BACKEND_ENDPOINT = os.getenv("BACKEND_ENDPOINT")
SPOTIFY_ENDPOINT = "https://accounts.spotify.com"

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = f"{BACKEND_ENDPOINT}/auth/success"

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/login") # TODO: maybe change to post later. 
async def spotify_login_for_access_token():
    """Go through spotify's login process, get user_id, tokenize, return token. """
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
async def auth_callback(request: Request) -> Token:
    auth_code = request.query_params.get("code")

    if not auth_code:
        return JSONResponse({"error": "No auth_code returned"}, status_code=400)

    # from auth_code, make refresh_token and access_token and spotify_user_id.
    # tokenize the spotify_user_id and send over. TODO: and the refresh token too? 
    refresh_token = create_refresh_token(auth_code=auth_code)
    access_token = create_access_token(refresh_token=refresh_token)
    spotify_user_id = create_spotify_user_id(access_token=access_token)

    # Store spotify_user_id and refresh_token in the database. In case it exists, just update it.
    await db_update(spotify_user_id, refresh_token)

    access_token = create_jwt_token(
        data={"sub": spotify_user_id}
    )
    return Token(access_token=access_token, token_type="bearer")

@router.get("/validate")
async def read_users_me(current_user: User = Depends(get_current_user)) -> User:
    '''For a token passed through the request body (Authorization Bearer), validate it.'''
    return current_user
