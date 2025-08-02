# Standard library imports
import json
import requests
from datetime import timedelta

# FastAPI imports
from fastapi import APIRouter, Header

# Third-party imports

# Local imports
from api.models import (
    PlaylistCreationRequest,
    PopulatePlaylistRequest,
    RemoveTracksRequest,
    ArtistSearchRequest,
)

# Global & Environment Variables


router = APIRouter(prefix="/api", tags=["api"])


@router.post("/playlist")
def create_playlist(payload: PlaylistCreationRequest, access_token: str = Header(...)):
    """
    Create a new playlist with a given name".
    """
    url = f"https://api.spotify.com/v1/users/{payload.spotify_user_id}/playlists"
    data = json.dumps(
        {
            "name": payload.playlist_name,
            "public": True,
            "description": "Created by https://github.com/shafwanur/spotify-track-sorter",
        }
    )
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    response = requests.post(url=url, data=data, headers=headers)

    playlist_id = response.json().get("id")

    if playlist_id:
        return {"playlist_id": playlist_id}


@router.post("/playlist/tracks")
def populate_playlist(
    payload: PopulatePlaylistRequest, access_token: str = Header(...)
):
    """
    Populate tracks to the specified playlist with playlist_id.
    """
    url = f"https://api.spotify.com/v1/playlists/{payload.playlist_id}/tracks"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    data = json.dumps({"uris": payload.uris})
    response = requests.post(url=url, headers=headers, data=data)
    return {
        "message": "Successfully populated playlist!",
        "status_code": response.status_code,
    }


@router.delete("/playlist/tracks")
def populate_playlist(payload: RemoveTracksRequest, access_token: str = Header(...)):
    """
    Populate tracks to the specified playlist with playlist_id.
    """
    url = f"https://api.spotify.com/v1/playlists/{payload.playlist_id}/tracks"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    # uris are received as a simple list of uris. converted here to how spotify expects it.
    payload.uris = [{"uri": uri} for uri in payload.uris]
    data = json.dumps({"tracks": payload.uris})
    response = requests.delete(url=url, headers=headers, data=data)
    return {
        "message": "Successfully deleted tracks!",
        "status_code": response.status_code,
    }


@router.get("/artists")
def search_artist(payload: ArtistSearchRequest, access_token: str = Header(...)):
    """
    Searches artist by name
    """
    url = f"https://api.spotify.com/v1/search"
    headers = {
        "Authorization": f"Bearer {access_token}",
    }
    params = {"q": payload.artist_name, "type": "artist", "limit": 5}
    response = requests.get(url=url, headers=headers, params=params)
    return {
        "status_code": response.status_code,
        "msg": response.json(),  # images from here will be useful later on, returning entire json.
    }
