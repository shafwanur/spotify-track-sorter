# Standard library imports
from datetime import timedelta

# FastAPI imports
from fastapi import APIRouter
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import Depends, HTTPException, status

# Third-party imports 
from sqlalchemy import text

# Local imports
from auth.helpers import authenticate_user, create_access_token, get_current_active_user, get_password_hash
from auth.models import Token, User
from db.init import engine

# Global & Environment Variables
ACCESS_TOKEN_EXPIRE_MINUTES = 30

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> Token:
    '''Try authenticating a user, on success return access_token'''
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

@router.post("/signup") # TODO: show when user already exists. should be handled better with proper sqlalchemy conventions.
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
        
@router.get("/me", response_model=User)
async def read_users_me(
    current_user: User = Depends(get_current_active_user),
):
    return current_user
