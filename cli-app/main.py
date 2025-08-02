from api import SpotifyAPI

api = SpotifyAPI(arg = "global-sort")

print("Enter the Spotify URL of the artist:", end = " ")
# url = input()
url = "https://open.spotify.com/artist/1moxjboGR7GNWYIMWsRjgG?si=lpBNIkuqTFm2A_USw9ADzg"

artist_id = url[url.rfind("/")+1:url.find("?")]

api.magic(artist_id = artist_id)