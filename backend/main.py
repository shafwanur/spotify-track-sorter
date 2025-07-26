import os
import random
import string
from urllib.parse import urlencode
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse, JSONResponse
from dotenv import load_dotenv

from db.init import init_db

# Load environment variables
load_dotenv()

CLIENT_ID = os.getenv("CLIENT_ID")
REDIRECT_URI = "http://localhost:8000/auth/success"

# Lifespan event for startup tasks
@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(lifespan=lifespan)

# Utility functions
def generate_random_string(length: int) -> str:
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def get_scopes() -> str:
    scopes = [
        'user-library-modify',
        'user-read-playback-position',
        'user-read-email',
        'user-library-read',
        'playlist-read-collaborative',
        'playlist-modify-private',
        'user-follow-read',
        'user-read-playback-state',
        'user-read-currently-playing',
        'user-read-private',
        'playlist-read-private',
        'user-top-read',
        'playlist-modify-public',
        'ugc-image-upload',
        'user-follow-modify',
        'user-modify-playback-state',
        'user-read-recently-played'
    ]
    return " ".join(scopes)

# API Endpoints

@app.get("/login")
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

@app.get("/auth/success")
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

@app.get("/items/{item_id}")
async def read_item(item_id):
    return {"item_id": item_id}
