import os
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# 1. Load the secret keys from your hidden .env file
load_dotenv()

# 2. Authenticate with Spotify using those keys
auth_manager = SpotifyClientCredentials(
    client_id=os.getenv('SPOTIPY_CLIENT_ID'),
    client_secret=os.getenv('SPOTIPY_CLIENT_SECRET')
)
sp = spotipy.Spotify(auth_manager=auth_manager)

# 3. Test a quick search query for your target song's playlists
query = "About You"
results = sp.search(q=query, type='playlist', limit=5)

# 4. Print the results to see if it works!
print(f"--- Top 5 Playlist Results for '{query}' ---")
for idx, playlist in enumerate(results['playlists']['items']):
    print(f"{idx + 1}. Name: {playlist['name']} | Owner: {playlist['owner']['display_name']}")