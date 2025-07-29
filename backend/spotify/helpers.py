import os
import base64
import random
import string
import requests
from dotenv import load_dotenv

from datetime import datetime, timedelta, timezone

from sqlalchemy import text # TODO: probably deprecated as fuck to use this. 

from db.init import engine 

# Global & Environment Variables
load_dotenv()

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
BACKEND_ENDPOINT = os.getenv("BACKEND_ENDPOINT")
SPOTIFY_ENDPOINT = os.getenv("SPOTIFY_ENDPOINT")
REDIRECT_URI = f"{BACKEND_ENDPOINT}/spotify/success" 

# Some util functions
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

# Actual spotify related helpers. TODO: update comment
def create_refresh_token(auth_code: str):
    # Exchange auth_code immediately for refresh_token
    url = f'{SPOTIFY_ENDPOINT}/api/token'
    data = {
        'grant_type': 'authorization_code',
        'code': auth_code,
        'redirect_uri': REDIRECT_URI
    }
    cred = f'{CLIENT_ID}:{CLIENT_SECRET}'
    cred_b64 = base64.b64encode(cred.encode())
    headers = {
        'Authorization': f'Basic {cred_b64.decode()}'
    }
    response = requests.post(url=url, data=data, headers=headers)
    return response.json().get('refresh_token') # TODO: returns None when it doesn't exist? 

def store_refresh_token(user_id: str, refresh_token: str):
    with engine.connect() as conn:
        insert_query = text("""
            INSERT INTO refresh_tokens (id, refresh_token)
            VALUES (:id, :refresh_token)
            ON CONFLICT (id) DO UPDATE SET refresh_token = :refresh_token
        """)
        conn.execute(insert_query, {"id": user_id, "refresh_token": refresh_token})
        conn.commit()

def get_refresh_token(user_id: str):
    with engine.connect() as conn:
        select_query = text("""
            SELECT refresh_token FROM refresh_tokens WHERE id = :id
        """)
        result = conn.execute(select_query, {"id": user_id}).fetchone()
        if result:
            refresh_token = result[0]
            return refresh_token

# Caching the access_token and storing it in memory
access_token_cache = {}

def cache_access_token(user_id: int, access_token: str, expires_in: int = 3600):
    access_token_cache[user_id] = {
        "access_token": access_token,
        "expires_at": datetime.now(timezone.utc) + timedelta(seconds=expires_in)
    }

def get_cached_access_token(user_id: int) -> str | None:
    token_data = access_token_cache.get(user_id)
    if token_data and token_data["expires_at"] > datetime.now(timezone.utc):
        return token_data["access_token"]
    return None

def create_access_token(user_id: str):
    url = f'{SPOTIFY_ENDPOINT}/api/token'                
    data = {
        'grant_type': 'refresh_token',
        'refresh_token': get_refresh_token(user_id) # Expecting its always there. could make a call to the api endpoint too, possibly unnecessary
    }
    cred = f'{CLIENT_ID}:{CLIENT_SECRET}'
    cred_b64 = base64.b64encode(cred.encode())
    headers = {
        'Authorization': f'Basic {cred_b64.decode()}'
    }
    response = requests.post(url = url, data = data, headers = headers)
    access_token = response.json().get('access_token')
    
    # Cache it 
    cache_access_token(user_id=user_id, access_token=access_token)

    # return
    return access_token

def create_spotify_user_id(access_token: str):
    url = f"https://api.spotify.com/v1/me"
    headers = {
        "Authorization": "Bearer " + access_token
    }
    response = requests.get(url, headers=headers) # TODO: some error handling
    spotify_user_id = response.json().get("id")
    return spotify_user_id

def get_spotify_user_id(user_id: str):
    with engine.connect() as conn:
        query = text("SELECT spotify_user_id FROM refresh_tokens WHERE id = :user_id")
        result = conn.execute(query, {"user_id": user_id}).fetchone()
        if result:
            return result[0]
        
def store_spotify_user_id(user_id: int, spotify_user_id: str):
    with engine.connect() as conn:
        update_query = text("""
            UPDATE refresh_tokens
            SET spotify_user_id = :spotify_user_id
            WHERE id = :user_id
        """)
        conn.execute(update_query, {"spotify_user_id": spotify_user_id, "user_id": user_id})
        conn.commit()