import pandas as pd
from collections import Counter
from itertools import combinations

DATA_PATH = "data/raw/spotify_playlists_dataset.csv"

print("Step 1: Load and clean columns:")
df = pd.read_csv(DATA_PATH, nrows=100000, escapechar='\\', on_bad_lines='skip')

# Get rid of double-quotes outside of column headers
df.columns = df.columns.str.replace('"', '').str.strip()

# Drop any rows that have blank/missing data in these columns
df = df.dropna(subset=['artistname', 'trackname', 'playlistname'])

# Also strip any stray quotes from the actual data inside the text columns
df['artistname'] = df['artistname'].astype(str).str.replace('"', '').str.strip()
df['trackname'] = df['trackname'].astype(str).str.replace('"', '').str.strip()
df['playlistname'] = df['playlistname'].astype(str).str.replace('"', '').str.strip()

# Combine artist + track into a single unique song label
df['song'] = df['artistname'] + " - " + df['trackname']

print(f"Successfully loaded {len(df)} rows.")
print("Columns are now clean:", df.columns.tolist())

print("\nStep 2: Grouping songs by playlist:")
print("Calculating track co-occurrences:")

# Group rows by playlist name
playlist_groups = df.groupby('playlistname')['song'].apply(list)

# Count song pairs
pair_counter = Counter()

for playlist, songs in playlist_groups.items():
    # Remove duplicate tracks and guarantee everything is a clean string
    unique_songs = list(set([str(s) for s in songs]))
    
    # If the playlist has at least 2 songs, find all possible pairs
    if len(unique_songs) > 1:
        for pair in combinations(sorted(unique_songs), 2):
            pair_counter[pair] += 1

print("Top 5 Most Co-Occurring Song Pairs (The Ultimate Vibe Matches):")
print("-" * 60)
for pair, count in pair_counter.most_common(5):
    print(f"🎵 {pair[0]} \n   🤝 {pair[1]} \n   Shared Playlists: {count}\n")
print("-" * 60)