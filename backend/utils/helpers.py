import random
import string

def generate_random_string(length: int) -> str:
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def get_scopes() -> str:
    scopes = [
        'user-library-modify',
        'user-read-playback-position',
        'user-read-username',
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