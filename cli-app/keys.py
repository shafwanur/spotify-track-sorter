import os
import webbrowser
from dotenv import load_dotenv

load_dotenv()

''' Secret Information '''
USER_ID = os.getenv('USER_ID')
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')

''' URL '''
REDIRECT_URI = 'https%3A%2F%2Fexample.com%2Fcallback'

scope = 'user-library-modify user-read-playback-position user-read-email user-library-read playlist-read-collaborative playlist-modify-private user-follow-read user-read-playback-state user-read-currently-playing user-read-private playlist-read-private user-top-read playlist-modify-public ugc-image-upload user-follow-modify user-modify-playback-state user-read-recently-played'
scope = scope.replace(' ', '%20')

url = f'https://accounts.spotify.com/authorize?client_id={CLIENT_ID}&response_type=code&redirect_uri={REDIRECT_URI}&scope={scope}&state=34fFs29kd09'

''' Open url in Browser, Extract from code='' '''
# webbrowser.open_new(url)

''' Extracted AUTH_CODE'''
AUTH_CODE = os.getenv('AUTH_CODE')
''' Receieved from SpotifyAPI.refresh_token() '''
REFRESH_TOKEN = os.getenv('REFRESH_TOKEN')