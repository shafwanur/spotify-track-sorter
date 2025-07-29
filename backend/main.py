from fastapi import FastAPI
from contextlib import asynccontextmanager
from db.init import init_db

import auth.routes as auth
import spotify.routes as spotify
import api.routes as api

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(lifespan=lifespan)

app.include_router(auth.router)
app.include_router(spotify.router)
app.include_router(api.router)