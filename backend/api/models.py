from pydantic import BaseModel


class PlaylistCreationRequest(BaseModel):
    playlist_name: str
    spotify_user_id: str


class PopulatePlaylistRequest(BaseModel):
    playlist_id: str
    uris: list


class RemoveTracksRequest(BaseModel):
    playlist_id: str
    uris: list


class ArtistSearchRequest(BaseModel):
    artist_name: str
