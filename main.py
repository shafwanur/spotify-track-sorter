from api import SpotifyAPI

api = SpotifyAPI(arg = "all-of")

print("Enter the Spotify URL of the artist:", end = " ")
# url = input()
url = "https://open.spotify.com/artist/6XyY86QOPPrYVGvF9ch6wz?si=Ycok5rqcTJSADDv-JwQ_Sg"

artist_id = url[url.rfind("/")+1:url.find("?")]

api.magic(artist_id = artist_id)