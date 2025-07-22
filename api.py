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
    # TODO: instrumentals, acapellas, etc. should be removed. live songs too? i don't like the current duplicate remover ...
    def __init__(self, arg: str):
        self.ACCESS_TOKEN = -1 # TODO: End Goal: self.ACCESS_TOKEN & self.TOKEN_TIME shall not be used like this anymore. Store them as environment variables.
        self.TOKEN_TIME = -1
        self.all_songs = []
        self.arg = arg

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

        # TODO: update to use a database
        with open('auth_info', 'w') as file:
            file.write(f'{self.ACCESS_TOKEN}\n{self.TOKEN_TIME}')

        return self.ACCESS_TOKEN

    def process_track(self, track_id = '5VSqvL5NLxBr7uMNfjwLt8'): # feelslikeimfallinginlove from Coldplay
        '''
        Processes a single track and returns its popularity, album name, release date, track name, and URI.
        '''
        
        url = f'https://api.spotify.com/v1/tracks/{track_id}'
        headers = {
            'Authorization': f'Bearer {self.access_token()}',
        }
        response = requests.get(url = url, headers = headers)
        if response.status_code == 200:
            response = response.json()
            return (response['popularity'], response['album']['name'], response['album']['release_date'], response['name'], response['uri'])

    def process_album_tracks(self, album_id = '1PdMoahMiMnqWfzWZs3xSI'): # Moon Music (Full Mood Edition) from Coldplay
        '''
        Process all tracks in an album and append them to the all_songs list.
        '''
        
        url = f'https://api.spotify.com/v1/albums/{album_id}/tracks'
        headers = {
            'Authorization': f'Bearer {self.access_token()}',
        }
        params = {
            'limit': 50,
        }
        response = requests.get(url = url, headers = headers, params = params)
        for item in response.json()['items']:
            self.all_songs.append(self.process_track(track_id = item['id']))
    
    def process_albums(self, artist_id = '4gzpq5DPGxSnKTe4SA8HAU'): # Coldplay
        '''
        Process all albums of an artist and the album's tracks.
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
                self.process_album_tracks(album_id = item['id'])
                print(f'Processed: {item['name']}') # album processed currently
        
            url = response.json()['next']
            if type(url) != str:
                break
        
    def create_playlist(self, artist_name = 'Coldplay'):
        '''
        Create a new playlist for the artist with the name "self.arg: {artist_name}".
        '''
        
        url = f'https://api.spotify.com/v1/users/{USER_ID}/playlists'
        data = json.dumps({
            'name': " ".join(w.capitalize() for w in self.arg.split('-')) + f": {artist_name}",
            'public': True,
            'description': f"All songs posted by {artist_name} on Spotify, sorted with the {self.arg} argument. Created with https://github.com/shafwanur/spotify-track-sorter"
        })
        headers = {
            'Authorization': f'Bearer {self.access_token()}',
            'Content-Type': 'application/json'
        }
        response = requests.post(url = url, data = data, headers = headers)
        print(f'Playlist for {artist_name} created with arg {self.arg} & id {response.json()['id']}')
        return response.json()['id']

    def add_track_to_playlist(self, playlist_id, uris):
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

    def sort_songs(self):
        '''
        Sort self.all_songs according to the argument passed. 

        Possible arguments: 
            global-sort: sort every song by popularity
            album-sort: albums sorted by year, songs within the album sorted.
            all-of: einfach nach der Reihenfolge der Veröffentlichung Songs in die Playlist reinhauen.

        At the end, there's a layer to delete duplicate songs. Here, the song stays in the album which is the largest. 
        '''
        
        # Types of Sorting available
        # Tuple Format: (popularity, albumname, releasedate, trackname, uri)
        if self.arg == "album-sort": 
            self.all_songs = sorted(self.all_songs, key = lambda x: (x[2], x[1], -x[0]))
        if self.arg == "global-sort": 
            self.all_songs = sorted(self.all_songs, key = lambda x : -x[0])
        if self.arg == "all-of": 
            self.all_songs = sorted(self.all_songs, key = lambda x : (x[2], x[1]))

        # Deleting Duplicates Layer
        songs_in_album = dict()
        for p in self.all_songs:
            songs_in_album[p[1]] = songs_in_album.get(p[1], 0) + 1

        song_album_mapping = dict()
        for p in sorted(self.all_songs, key = lambda x: (x[3], -songs_in_album[x[1]])):
            song_name = p[3]
            if song_name not in song_album_mapping:
                song_album_mapping[song_name] = p[1] # p[1] is the albumname

        without_dups = [] # without the duplicates
        for p in self.all_songs:
            songname, albumname = p[3], p[1]
            if song_album_mapping[songname] == albumname:
                without_dups.append(p)

        self.all_songs[:] = without_dups
        
    def magic(self, artist_id = '4gzpq5DPGxSnKTe4SA8HAU'): # Coldplay
        # TODO: need to update the logic here, make it übersichtlicher than just being "magic"
        '''
        Main function to process the artist's albums, create a playlist, and add all songs to it.
        '''

        # Get name of the artist from artist_id
        artist_name = self.get_artist_name(artist_id)

        # Create the playlist, get its id
        playlist_id = self.create_playlist(artist_name)

        # Process all albums of the artist
        self.process_albums(artist_id)

        print(f"Song Count: {len(self.all_songs)} \nSorted Songs: ") 

        # Sort self.all_songs
        self.sort_songs()

        # Printing some stats

        uris = [] # extracting just the uris in this step to later use to push into the newly created playlist
        file_name = os.path.join("stats", f"{artist_name}.txt")
        with open(file_name, 'a', encoding='utf-8') as file:
            for song in self.all_songs:
                uris.append(song[-1])
                print(song)
                file.write(f"{song}\n")
        
        # Actual pushing the songs into the newly created playlist
        # TODO: should probably be a function on its own
        block_size = 100
        i = 0
        while i <= len(self.all_songs):
            self.add_track_to_playlist(playlist_id, uris[i:i+block_size])
            i += block_size
        
        # Success
        print(f"Success: All {len(self.all_songs)} songs added to playlist {playlist_id}")
    