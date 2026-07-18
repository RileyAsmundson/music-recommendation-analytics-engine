import pandas as pd
import sqlite3
import os

# 1. Setup paths
RAW_DATA_PATH = "data/raw/spotify_playlists_dataset.csv"
DB_PATH = "data/processed/vibe_warehouse.db"

# Ensure the processed folder exists
os.makedirs("data/processed", exist_ok=True)

# 2. Connect to local SQLite database
print(f"Connecting to database at {DB_PATH}...")
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Clear out any old staging data if the script stopped halfway previously
cursor.execute("DROP TABLE IF EXISTS staging_raw")

# 3. Process the raw data in manageable chunks
print("Cleaning raw data and moving to staging table...")
chunk_size = 250000
row_count = 0

for chunk in pd.read_csv(RAW_DATA_PATH, escapechar='\\', on_bad_lines='skip', chunksize=chunk_size):
    # Clean headers
    chunk.columns = chunk.columns.str.replace('"', '').str.strip()
    
    # Drop rows with blank/corrupt data
    chunk = chunk.dropna(subset=['user_id', 'artistname', 'trackname', 'playlistname'])
    
    # Clean quotes out of the text columns
    chunk['artistname'] = chunk['artistname'].astype(str).str.replace('"', '').str.strip()
    chunk['trackname'] = chunk['trackname'].astype(str).str.replace('"', '').str.strip()
    chunk['playlistname'] = chunk['playlistname'].astype(str).str.replace('"', '').str.strip()
    
    # Append this clean chunk into a temporary staging table in our database
    chunk.to_sql("staging_raw", conn, if_exists="append", index=False)
    
    row_count += len(chunk)
    print(f"   ...cleaned and staged {row_count:,} rows")

print("\nBuilding Normalized Data Warehouse Tables...")

# 4. Create and populate USERS table
print("   -> Building USERS table...")
cursor.executescript("""
    CREATE TABLE IF NOT EXISTS users (
        user_id TEXT PRIMARY KEY
    );
    INSERT OR IGNORE INTO users (user_id) 
    SELECT DISTINCT user_id FROM staging_raw;
""")

# 5. Create and populate TRACKS table
print("   -> Building TRACKS table...")
cursor.executescript("""
    CREATE TABLE IF NOT EXISTS tracks (
        track_id INTEGER PRIMARY KEY AUTOINCREMENT,
        artist_name TEXT,
        track_name TEXT,
        UNIQUE(artist_name, track_name)
    );
    INSERT OR IGNORE INTO tracks (artist_name, track_name)
    SELECT DISTINCT artistname, trackname FROM staging_raw;
""")

# 6. Create and populate PLAYLISTS table
print("   -> Building PLAYLISTS table...")
cursor.executescript("""
    CREATE TABLE IF NOT EXISTS playlists (
        playlist_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        playlist_name TEXT,
        UNIQUE(user_id, playlist_name)
    );
    INSERT OR IGNORE INTO playlists (user_id, playlist_name)
    SELECT DISTINCT user_id, playlistname FROM staging_raw;
""")

# 7. Create the PLAYLIST_TRACKS junction table
print("   -> Linking it all together in PLAYLIST_TRACKS...")
cursor.executescript("""
    CREATE TABLE IF NOT EXISTS playlist_tracks (
        playlist_id INTEGER,
        track_id INTEGER,
        FOREIGN KEY(playlist_id) REFERENCES playlists(playlist_id),
        FOREIGN KEY(track_id) REFERENCES tracks(track_id),
        UNIQUE(playlist_id, track_id)
    );
    
    INSERT OR IGNORE INTO playlist_tracks (playlist_id, track_id)
    SELECT p.playlist_id, t.track_id
    FROM staging_raw s
    JOIN playlists p ON s.user_id = p.user_id AND s.playlistname = p.playlist_name
    JOIN tracks t ON s.artistname = t.artist_name AND s.trackname = t.track_name;
""")

# 8. Create Indexes for querying later
print("Creating database indexes for speed...")
cursor.executescript("""
    CREATE INDEX IF NOT EXISTS idx_pt_playlist ON playlist_tracks(playlist_id);
    CREATE INDEX IF NOT EXISTS idx_pt_track ON playlist_tracks(track_id);
""")

# 9. Clean up the massive staging table to save hard drive space
print("Dropping temporary staging data...")
cursor.execute("DROP TABLE staging_raw")
conn.commit()
conn.close()

print("\nDATA WAREHOUSE BUILT SUCCESSFULLY!")