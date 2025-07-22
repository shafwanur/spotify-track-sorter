import random

albums = [
    ("Alpha", "2020-01-01"),
    ("Beta", "2021-06-15"),
    ("Gamma", "2022-11-30")
]

demo_data = []

for i in range(20):
    album_name, release_date = albums[random.randint(0, 2)]
    popularity = random.randint(0, 100)
    track_name = f"Track {random.randint(0, 10)}"
    uri = f"spotify:track:dummy{i+1:02d}"
    
    demo_data.append((popularity, album_name, release_date, track_name, uri))


# Sorting Layer
demo_data = sorted(demo_data, key = lambda x: (x[2], x[1]))

# Find songs in album stat
'''A is a list of tuples in the order of popularity, albumname, releasedate, trackname, uri'''
songs_in_album = dict()
for p in demo_data:
    songs_in_album[p[1]] = songs_in_album.get(p[1], 0) + 1

# See album song frequency
print(songs_in_album)

for p in sorted(demo_data, key = lambda x: (x[3], -songs_in_album[x[1]])):
   print(p)
      

song_album_mapping = dict()
for p in sorted(demo_data, key = lambda x: (x[3], -songs_in_album[x[1]])):
    song_name = p[3]
    if song_name not in song_album_mapping:
       song_album_mapping[song_name] = p[1] # p[1] is the albumname

print("Song album mapping")
for p in song_album_mapping:
    print(p, song_album_mapping[p])
    
new_demo_data = [] # without the duplicates
for p in demo_data:
    songname, album_name = p[3], p[1]
    if song_album_mapping[songname] == album_name:
      new_demo_data.append(p)

print("DEMO")
for p in new_demo_data:
    print(p)