import os
import json
import base64
import requests
import datetime

from keys import USER_ID
from keys import AUTH_CODE
from keys import CLIENT_ID
from keys import CLIENT_SECRET
from keys import REFRESH_TOKEN

class SpotifyAPI:
    def __init__(self):
        self.ACCESS_TOKEN = -1
        self.TOKEN_TIME = -1
        self.all_songs = []

    def refresh_token(self):
        url = 'https://accounts.spotify.com/api/token'
        data = {
            'grant_type': 'authorization_code',
            'code': AUTH_CODE,
            'redirect_uri': 'https://example.com/callback'
        }
        cred = f'{CLIENT_ID}:{CLIENT_SECRET}'
        cred_b64 = base64.b64encode(cred.encode())
        headers = {
            'Authorization': f'Basic {cred_b64.decode()}'
        }
        ret = requests.post(url = url, data = data, headers = headers)
        return ret.json()['refresh_token']

    def access_token(self):
        with open('auth_info', 'r') as file:
            data = file.readlines()

        self.ACCESS_TOKEN = data[0].replace("\n", "")
        self.TOKEN_TIME = datetime.datetime.strptime(data[1].replace("\n", ""), '%Y-%m-%d %H:%M:%S.%f')

        if self.ACCESS_TOKEN == '-1' or (datetime.datetime.now() - self.TOKEN_TIME).total_seconds() > 3600:
            url = 'https://accounts.spotify.com/api/token'                
            data = {
                'grant_type': 'refresh_token',
                'refresh_token': REFRESH_TOKEN
            }
            cred = f'{CLIENT_ID}:{CLIENT_SECRET}'
            cred_b64 = base64.b64encode(cred.encode())
            headers = {
                'Authorization': f'Basic {cred_b64.decode()}'
            }
            ret = requests.post(url = url, data = data, headers = headers)
            self.ACCESS_TOKEN = ret.json()['access_token']
            self.TOKEN_TIME = datetime.datetime.now()

        with open('auth_info', 'w') as file:
            file.write(f'{self.ACCESS_TOKEN}\n{self.TOKEN_TIME}')

        return self.ACCESS_TOKEN

    def process_track(self, track_id = '5VSqvL5NLxBr7uMNfjwLt8'): # feelslikeimfallinginlove from Coldplay
        '''
        Get a single track and return its popularity, album name, track name, and URI.
        '''
        
        url = f'https://api.spotify.com/v1/tracks/{track_id}'
        headers = {
            'Authorization': f'Bearer {self.access_token()}',
        }
        response = requests.get(url = url, headers = headers)
        if response.status_code == 200:
            response = response.json()
            return (response['popularity'], response['album']['name'], response['name'], response['uri'])

    def process_tracks(self, album_id = '1PdMoahMiMnqWfzWZs3xSI'): # Moon Music (Full Mood Edition) from Coldplay
        '''
        Get all tracks in an album and append them to the all_songs list.
        '''
        
        url = f'https://api.spotify.com/v1/albums/{album_id}/tracks'
        headers = {
            'Authorization': f'Bearer {self.access_token()}',
        }
        params = {
            'limit': 50,
        }
        response = requests.get(url = url, headers = headers, params = params)
        tmp_array = []
        for item in response.json()['items']:
            tmp_array.append(self.process_track(track_id = item['id']))
        
        tmp_array.sort()
        tmp_array = list(reversed(tmp_array))
        self.all_songs.extend(tmp_array)
    
    def process_albums(self, artist_id = '4gzpq5DPGxSnKTe4SA8HAU'): # Coldplay
        '''
        Get all albums of an artist and process each album's tracks.
        '''
        
        url = f'https://api.spotify.com/v1/artists/{artist_id}/albums'
        headers = {
            'Authorization': f'Bearer {self.access_token()}',
        }
        params = {
            'include_groups': "album,single",
            'limit': 50,
        }
        while True:
            response = requests.get(url = url, headers = headers, params = params)
            items = response.json()['items']
            for item in items:
                self.process_tracks(album_id = item['id'])
                print(f'Processed: {item['name']}') # album processed currently
        
            url = response.json()['next']
            if type(url) != str:
                break
        
    def create_playlist(self, artist_name = 'Coldplay'):
        '''
        Create a new playlist for the artist with the name "All Of: {artist_name}".
        '''
        
        url = f'https://api.spotify.com/v1/users/{USER_ID}/playlists'
        data = json.dumps({
            'name': f'All Of: {artist_name}',
            'public': True,
            'description': f"All songs posted by {artist_name} on Spotify, sorted by popularity. Created with https://github.com/shafwanur/spotify-track-sorter"
        })
        headers = {
            'Authorization': f'Bearer {self.access_token()}',
            'Content-Type': 'application/json'
        }
        response = requests.post(url = url, data = data, headers = headers)
        print(f'Playlist for {artist_name} created with id {response.json()['id']}')
        return response.json()['id']

    def add_to_playlist(self, playlist_id, uris):
        '''
        Add tracks to the specified playlist with playlist_id.
        '''

        url = f'https://api.spotify.com/v1/playlists/{playlist_id}/tracks'
        headers = {
            'Authorization': f'Bearer {self.access_token()}',
            'Content-Type': 'application/json'
        }
        data = json.dumps({
            'uris': uris
        })
        response = requests.post(url = url, headers = headers, data = data)
        if response.status_code == 200:
            print("Success: Playlist Add")
    
    def get_artist_name(self, artist_id):
        '''
        Get the name of the artist using their ID.
        '''
        
        url = f'https://api.spotify.com/v1/artists/{artist_id}'
        headers = {
            'Authorization': f'Bearer {self.access_token()}',
            'Content-Type': 'application/json'
        }
        response = requests.get(url = url, headers = headers)
        return response.json()['name']

    def sorted_songs(self, artist_id):
        # TODO: implement later.
        pass

    def magic(self, artist_id = '4gzpq5DPGxSnKTe4SA8HAU'): # Coldplay
        '''
        Main function to process the artist's albums, create a playlist, and add all songs to it.
        '''

        artist_name = self.get_artist_name(artist_id)
        playlist_id = self.create_playlist(artist_name)
        self.process_albums(artist_id)
        print(f"Song Count: {len(self.all_songs)}") 
        print(self.all_songs[:10])

        print("Songs Sorted: ")
        uris = []

        file_name = os.path.join("stats", f"{artist_name}.txt")
        with open(file_name, 'a', encoding='utf-8') as file:
            for song in self.all_songs:
                uris.append(song[-1])
                print(song)
                file.write(f"{song}\n")
        
        block_size = 100
        i = 0
        while i <= len(self.all_songs):
            self.add_to_playlist(playlist_id, uris[i:i+block_size])
            i += block_size
        
        print(f"Success: All {len(self.all_songs)} songs added to playlist {playlist_id}")
    