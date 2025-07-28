# Standard library imports
import os
from urllib.parse import urlencode

# FastAPI imports
from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse, JSONResponse

# Third-party library imports 
from dotenv import load_dotenv

# Local imports
from auth.helpers import authenticate_user, create_access_token
from auth.models import Token
from utils.helpers import generate_random_string, get_scopes

# Global & Environment Variables
load_dotenv()

CLIENT_ID = os.getenv("CLIENT_ID")
REDIRECT_URI = "http://localhost:8000/spotify/success" # TODO: make better, hard-coded, look ugly

router = APIRouter(prefix="/spotify", tags=["spotify"])


@router.get("/login")
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
    auth_url = "https://accounts.spotify.com/authorize?" + urlencode(query_params)
    return RedirectResponse(auth_url)

@router.get("/success")
def auth_callback(request: Request):
    code = request.query_params.get("code")
    state = request.query_params.get("state")
    if not code:
        return JSONResponse({"error": "No code returned"}, status_code=400)
    return JSONResponse({
        "message": "Authorization successful",
        "code": code,
        "state": state
    })