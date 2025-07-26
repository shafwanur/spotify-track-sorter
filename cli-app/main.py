from api import SpotifyAPI

api = SpotifyAPI(arg = "album-sort")

print("Enter the Spotify URL of the artist:", end = " ")
# url = input()
url = "https://open.spotify.com/artist/53XhwfbYqKCa1cC15pYq2q?si=5_0Sym8GRnO3-jFBos3RFw"

artist_id = url[url.rfind("/")+1:url.find("?")]

api.magic(artist_id = artist_id)