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
        self.DONE = dict()
        self.GENRES = dict() 
        self.PLAYLISTS = dict()
            
        with open('genres.txt', 'r') as file:
            for s in file:
                s = s.split(',')
                id = s.pop(0)
                self.GENRES[id] = s
        
        self.PLAYLISTS['other'] = '' # playlist for dumping outcasts
        with open('playlists.txt', 'r') as file:
            for s in file:
                s = list(s.split())
                value = s.pop(-1)
                key = ' '.join(s)
                self.PLAYLISTS[key] = value

        with open('done.txt', 'r') as file:
            for s in file:
                s = s.replace('\n', '')
                self.DONE[s] = True

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
    
    def info(self, type, id = -1):
        if type == 'Song':
            url = f'https://api.spotify.com/v1/tracks/{id}'
            headers = {
                'Authorization': f'Bearer {self.access_token()}',
            }
            ret = requests.get(url = url, headers = headers)
            return ret.json()

    def genres(self, id):
        song = self.info('Song', id = id)
        headers = {
            'Authorization': f'Bearer {self.access_token()}',
        }
        g = []
        albumID = song['album']['id']
        if self.GENRES.get(albumID, -1) == -1:
            obj = requests.get(url = song['album']['href'], headers = headers).json()
            self.GENRES[albumID] = obj['genres']

            with open('genres.txt', 'a') as file:
                s = ','.join(map(str, self.GENRES[albumID]))
                file.write(f'{albumID},{s}\n')

        g.extend(self.GENRES[albumID])

        for p in song['artists']:
            artistID = p['id']
            if self.GENRES.get(artistID, -1) == -1:
                url = p['href'] 
                obj = requests.get(url = url, headers = headers).json()
                self.GENRES[artistID] = obj['genres']
                with open('genres.txt', 'a') as file:
                    s = ','.join(map(str, self.GENRES[artistID]))
                    file.write(f'{artistID},{s}\n')

            g.extend(self.GENRES[artistID])

        g = list(map(str.strip, g))
        return list(set(g))

    def playlistID(self, name): 
        if self.PLAYLISTS.get(name, -1) == -1:
            url = f'https://api.spotify.com/v1/users/{USER_ID}/playlists'
            data = json.dumps({
                'name': name,
                'public': True
            })
            headers = {
                'Authorization': f'Bearer {self.access_token()}',
                'Content-Type': 'application/json'
            }
            ret = requests.post(url = url, data = data, headers = headers)

            if ret.status_code != 200 and ret.status_code != 201:
                return self.PLAYLISTS['other']

            id = ret.json()['id']
            self.PLAYLISTS[name] = id

            with open('playlists.txt', 'a') as file:
                file.write(f'{name} {id}\n')

        return self.PLAYLISTS[name]
    
    def add(self, pID, a):
        url = f'https://api.spotify.com/v1/playlists/{pID}/tracks'
        headers = {
            'Authorization': f'Bearer {self.access_token()}',
            'Content-Type': 'application/json'
        }
        data = json.dumps({
            'uris': a
        })
        ret = requests.post(url = url, headers = headers, data = data)

    def getlib(self):
        url = 'https://api.spotify.com/v1/me/tracks'
        headers = {
            'Authorization': f'Bearer {self.access_token()}',
        }
        params = {
            'limit': 50,
            'offset': 0
        }
        songs = dict()
        while True:
            broke = False
            ret = requests.get(url = url, headers = headers, params = params)
            for p in ret.json()['items']:
                id = p['track']['id']
                name = p['track']['name']
                print(id, name)
                if self.DONE.get(id, -1) != -1:
                    broke = True
                    break
                
                songs[id] = name

            url = ret.json()['next']
            if broke or type(url) != str:
                break
        
        return songs

    def categorise(self, songs):
        cat = dict()
        for p in songs:
            print(f'Processing {p}')
            g = self.genres(p)
            for genre in g:
                if cat.get(genre) == None:
                    cat[genre] = []

                cat[genre].append('spotify:track:' + p)

            self.DONE[p] = True
            with open('done.txt', 'a') as file:
                file.write(f'{p}\n')
        
        return cat
        
    def sort(self):
        songs = self.getlib()
        cat = self.categorise(songs)
        for genre in cat:
            new = self.PLAYLISTS.get(genre, -1) == -1
            noun = 'songs' if len(cat[genre]) > 1 else 'song'
            if new:
                print(f'\nCreate new playlist {genre}? {len(cat[genre])} {noun} will be added: ')
            else:
                print(f'\nAdd songs to {genre}? {len(cat[genre])} {noun} will be added: ')

            for s in cat[genre]:
                name = songs[s.split('spotify:track:')[-1]]
                print(name)
            
            res = input('[y/n]? ').lower()
            if res == 'y':
                id = self.playlistID(genre)
                i = 0
                while i < len(cat[genre]):
                    self.add(id, cat[genre][i:i + 100])
                    i += 100
                
                print('Added Successfully!')

api = SpotifyAPI()
api.sort()
