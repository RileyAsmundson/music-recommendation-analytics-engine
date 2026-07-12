import os
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth 

load_dotenv()

auth_manager = SpotifyOAuth(
    client_id=os.getenv('SPOTIPY_CLIENT_ID'),
    client_secret=os.getenv('SPOTIPY_CLIENT_SECRET'),
    redirect_uri="http://127.0.0.1:8080",
    scope="playlist-read-private"          # Permission to read the tracks
)
sp = spotipy.Spotify(auth_manager=auth_manager)

# Testing playlists
target_playlists = [
    '68YoePwZVmHztCf8D9t5B5',  # = Face Straight Out a Magazine (personal playlist)
    '6mql22Biv8sWpIRXaUtMOk'   # = 2 (personal playlist)
]

print("Exctracting Playlists...\n")

# Loop through each playlist
for playlist_id in target_playlists:

    # Grab the playlist name
    playlist_meta = sp.playlist(playlist_id, fields="name")
    playlist_name = playlist_meta.get('name', 'Unknown Playlist')
    
    print(f"Playlist: {playlist_name}")
    print("-" * 40)
    
    # Grab the tracks
    results = sp.playlist_tracks(playlist_id)
    tracks_list = results.get('items', [])
    
    # Loop through and print
    for list_item in tracks_list:
        
        # Need to check for both the  'item' key and the old 'track' key
        track = list_item.get('item') or list_item.get('track')
        
        if track: 
            track_id = track.get('id')
            track_name = track.get('name')
            
            artists = track.get('artists')
            artist_name = artists[0]['name'] if artists else "Unknown Artist"
            
            print(f"   ↳ 🎵 {track_name} — {artist_name} (ID: {track_id})")
            
    print("\n" + "="*40 + "\n")