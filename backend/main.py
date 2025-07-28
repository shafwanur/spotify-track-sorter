# Standard library imports
import os
import random
import string
from urllib.parse import urlencode
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone

# Third-party library imports
from dotenv import load_dotenv
from passlib.context import CryptContext
from pydantic import BaseModel
import jwt
from jwt.exceptions import InvalidTokenError
from sqlalchemy import text

# FastAPI imports
from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

# Local application imports
from db.init import init_db, engine

# Load environment variables
load_dotenv()

CLIENT_ID = os.getenv("CLIENT_ID")
REDIRECT_URI = "http://localhost:8000/auth/success"
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

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
        'user-read-username',
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

# --- OAuth2 and User Models ---

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None

class User(BaseModel):
    username: str | None = None
    disabled: str | None = None

class UserInDB(User):
    hashed_password: str

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# --- User Auth Helpers ---
def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_user(username: str):
    with engine.connect() as conn: 
        query = text("SELECT * FROM users WHERE username = :username")
        result = conn.execute(query, {"username": username}).fetchone()
        if result:
            row = result._mapping
            return UserInDB(username=row["username"], hashed_password=row["password"])

def authenticate_user(username: str, password: str):
    user = get_user(username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
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
    user = get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(
    current_user: User = Depends(get_current_user),
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

# --- Spotify API Endpoints ---
@app.get("/spotify/login")
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

# Other API Endpoints
@app.post("/users/signup")
async def create_user(username: str, password: str):
    password = get_password_hash(password)
    with engine.connect() as conn: 
        query = insert_query = text("""
            INSERT INTO users (username, password)
            VALUES (:username, :password)
        """)
        conn.execute(insert_query, {"username": username, "password": password})
        conn.commit()
        return {
            "message": f"User {username} created successfully."
        }
        

@app.post("/token")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> Token:
    user = authenticate_user(username=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")

@app.get("/users/me/", response_model=User)
async def read_users_me(
    current_user: User = Depends(get_current_active_user),
):
    return current_user

@app.get("/users/me/items/")
async def read_own_items(
    current_user: User = Depends(get_current_active_user),
):
    return [{"item_id": "Foo", "owner": current_user.username}]


