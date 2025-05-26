from api import SpotifyAPI

api = SpotifyAPI()

print("Enter the Spotify URL of the artist:", end = " ")
url = input()
# url = "https://open.spotify.com/artist/5Rl15oVamLq7FbSb0NNBNy?si=PC7iNNfhS3CBrB5mVTOdiw"
artist_id = url[url.rfind("/")+1:url.find("?")]

api.magic(artist_id)