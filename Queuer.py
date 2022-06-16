import spotipy
import spotipy.util as util

scope = 'playlist-modify-public'


username = "zt7ijumcftx641whk2cdo8es6"

#Auth token
token = util.prompt_for_user_token(username,scope,client_id='f83f7a4ca59240329d98fa301fc5b226',client_secret='64f9a510ca7f489197b728fcf017fb82',redirect_uri='https://spotify.com/')


#Create spotify object
sp = spotipy.Spotify(auth=token)

playlists = sp.user_playlists(username)

def get_playlist_tracks(playlist_id):
    """
    Get the playlist tracks
    :param playlist_id: playlist id
    :return: list of tracks
    """
    r = sp.user_playlist_tracks(username, playlist_id)
    t = r['items']
    ids = []
    while r['next']:
        r = sp.next(r)
        t.extend(r['items'])
    for s in t:
        ids.append(s["track"]["uri"])

    return ids

def get_playlist_artists(playlist_id):
    """
    Get artists of this playlist
    :param playlist_id: playlsit id
    :return: list of artists
    """
    r = sp.user_playlist_tracks(username,playlist_id)
    t = r['items']
    ids = []
    while r['next']:
        r = sp.next(r)
        t.extend(r['items'])
    for s in t:
        ids.append(s["track"]["album"]['artists'][0]['name'])


    return ids

def get_playlist_genre(playlist_id):
    """
    Get genre of the artists in this album
    :param playlist_id: playlist id
    :return: list of genres
    """
    r = sp.user_playlist_tracks(username,playlist_id)
    ids = []
    t = r['items']
    while r['next']:
        r = sp.next(r)
        t.extend(r['items'])
    for s in t:
        tmp = s["track"]["artists"][0]["external_urls"]["spotify"]
        artist = sp.artist(tmp)
        ids.append(artist["genres"])

    return ids

playlist_tracks = []
for playlist in playlists['items']:

    playlist_id = playlist['id']
    for item in get_playlist_tracks(playlist_id):
        playlist_tracks.append(item)

print (playlist_tracks)
#create a dict of how many songs are by the same artist
artists = {}
for playlist in playlists['items']:

    playlist_id = playlist['id']
    for item in get_playlist_artists(playlist_id):
        if item not in artists.keys():
            artists[item] = 1
        else:
            artists[item] += 1

artists = sorted(artists.items(), key=lambda x: x[1], reverse=True)
artists = dict(artists)
print(artists)
queue = []

def current_song():

    #Get current song information
    current_song_artist = sp.currently_playing()['item']['album']['artists'][0]['name']
    current_song_artist_url = sp.currently_playing()['item']['album']['artists'][0]['external_urls']['spotify']
    current_artist = sp.artist(current_song_artist_url)
    current_genres = current_artist['genres']

    #getting artists similar to current song artist and searches for a track in their top albums
    recommend_artist = sp.artist_related_artists(current_song_artist_url)
    matched_artist_genre = []
    for artist in recommend_artist['artists']:
        for artist_genre in artist['genres']:
            if artist_genre in current_genres:
                matched_artist_genre.append(artist)
    list_of_track_uris = []
    for artist in matched_artist_genre:
        top_tracks = sp.artist_top_tracks(artist['external_urls']['spotify'])
        track_uris = top_tracks['tracks'][0]['uri']
        list_of_track_uris.append(track_uris)

    for item in list_of_track_uris:
        if item not in playlist_tracks:
            if item not in track_uris:
                if item not in queue:
                    sp.add_to_queue(item)
                    queue.append(item)


while True:
    current_song()

