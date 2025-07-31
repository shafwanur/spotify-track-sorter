# Standard library imports
import base64
import os
from datetime import datetime, timedelta, timezone
import random
import string

# Third-party library imports
from dotenv import load_dotenv
from passlib.context import CryptContext
import jwt
from jwt.exceptions import InvalidTokenError
import requests
from sqlalchemy import text

# FastAPI imports
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

# Local imports
from db.init import engine
from auth.models import User, UserInDB, TokenData

# Global & Environment variables
load_dotenv()
BACKEND_ENDPOINT = os.getenv("BACKEND_ENDPOINT")
SPOTIFY_ENDPOINT = "https://accounts.spotify.com"

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = f"{BACKEND_ENDPOINT}/auth/success"

ACCESS_TOKEN_EXPIRE_MINUTES = 120
ALGORITHM = os.getenv("ALGORITHM")
SECRET_KEY = os.getenv("SECRET_KEY")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Some util functions
def generate_random_string(length: int) -> str:
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))

def get_scopes() -> str:
    scopes = [
        "user-library-modify",
        "user-read-playback-position",
        "user-read-email",
        "user-library-read",
        "playlist-read-collaborative",
        "playlist-modify-private",
        "user-follow-read",
        "user-read-playback-state",
        "user-read-currently-playing",
        "user-read-private",
        "playlist-read-private",
        "user-top-read",
        "playlist-modify-public",
        "ugc-image-upload",
        "user-follow-modify",
        "user-modify-playback-state",
        "user-read-recently-played",
    ]
    return " ".join(scopes)


def create_jwt_token(data: dict):
    """
    Create a jwt token with {data}
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES) # setting a default expiration for all tokens
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)):  
    # Expects token to be passed from the request header ("Authorization": Bearer Token)
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception
    
    return {"spotify_user_id": username}

# --- New Auth Method Helpers ---
def create_refresh_token(auth_code: str):
    # Exchange auth_code immediately for refresh_token
    url = f"{SPOTIFY_ENDPOINT}/api/token"
    data = {
        "grant_type": "authorization_code",
        "code": auth_code,
        "redirect_uri": REDIRECT_URI,
    }
    cred = f"{CLIENT_ID}:{CLIENT_SECRET}"
    cred_b64 = base64.b64encode(cred.encode())
    headers = {"Authorization": f"Basic {cred_b64.decode()}"}
    response = requests.post(url=url, data=data, headers=headers)
    AUTH_SUCCESS_FLAG = 1
    return response.json().get("refresh_token", None)  

def create_access_token(refresh_token: str = None): # TODO: cache this shit! 
    if refresh_token is None: 
        pass # TODO: when the fuck will it be None? never? 

    url = f"{SPOTIFY_ENDPOINT}/api/token"
    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token
    }
    cred = f"{CLIENT_ID}:{CLIENT_SECRET}"
    cred_b64 = base64.b64encode(cred.encode())
    headers = {"Authorization": f"Basic {cred_b64.decode()}"}
    response = requests.post(url=url, data=data, headers=headers)
    access_token = response.json().get("access_token")
    return access_token

def create_spotify_user(access_token: str):
    url = f"https://api.spotify.com/v1/me"
    headers = {"Authorization": "Bearer " + access_token}
    response = requests.get(url, headers=headers)  # TODO: add some error handling
    spotify_user_id = response.json().get("id")
    return spotify_user_id