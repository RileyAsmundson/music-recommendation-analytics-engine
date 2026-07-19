import sqlite3
import os
import sys

DB_PATH = "data/processed/vibe_warehouse.db"

def build_bi_summary_tables():
    print("Connecting to database...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Enable fast write-ahead logging
    cursor.execute("PRAGMA journal_mode = WAL;")
    cursor.execute("PRAGMA synchronous = OFF;")

    print("Step 1: Creating a temporary table for track playlist counts...")
    cursor.execute("DROP TABLE IF EXISTS tmp_track_counts;")
    cursor.execute("""
        CREATE TABLE tmp_track_counts AS
        SELECT track_id, COUNT(playlist_id) as playlist_count
        FROM playlist_tracks
        GROUP BY track_id;
    """)
    cursor.execute("CREATE UNIQUE INDEX idx_tmp_track_id ON tmp_track_counts(track_id);")

    print("Step 2: Initializing the BI similarity summary table...")
    cursor.execute("DROP TABLE IF EXISTS bi_track_similarities;")
    cursor.execute("""
        CREATE TABLE bi_track_similarities (
            seed_track_id INTEGER,
            match_track_id INTEGER,
            jaccard_score REAL,
            PRIMARY KEY (seed_track_id, match_track_id)
        );
    """)

    # Only process tracks that appear in 5+ playlists.
    print("Step 3: Fetching meaningful seed tracks (playlist presence >= 5)...")
    cursor.execute("SELECT track_id FROM tmp_track_counts WHERE playlist_count >= 5;")
    seed_tracks = [row[0] for row in cursor.fetchall()]
    total_tracks = len(seed_tracks)
    print(f"-> Found {total_tracks:,} meaningful tracks to process.")

    print("Step 4: Commencing fast-batch aggregation...")
    batch_size = 500
    for i in range(0, total_tracks, batch_size):
        batch = seed_tracks[i:i + batch_size]
        
        # We only pass a small batch of tracks into the heavy JOIN at one time
        cursor.execute(f"""
            INSERT OR IGNORE INTO bi_track_similarities (seed_track_id, match_track_id, jaccard_score)
            SELECT 
                pt1.track_id AS seed_track_id,
                pt2.track_id AS match_track_id,
                (CAST(COUNT(pt1.playlist_id) AS REAL) / (tc1.playlist_count + tc2.playlist_count - COUNT(pt1.playlist_id))) AS jaccard_score
            FROM playlist_tracks pt1
            JOIN playlist_tracks pt2 ON pt1.playlist_id = pt2.playlist_id AND pt1.track_id != pt2.track_id
            JOIN tmp_track_counts tc1 ON pt1.track_id = tc1.track_id
            JOIN tmp_track_counts tc2 ON pt2.track_id = tc2.track_id
            WHERE pt1.track_id IN ({','.join(['?']*len(batch))})
            GROUP BY pt1.track_id, pt2.track_id
            HAVING COUNT(pt1.playlist_id) >= 2;
        """, batch)
        
        # Commit every batch to disk instantly, keeping RAM clear
        conn.commit()
        
        # Print a live-updating progress bar
        progress = min(i + batch_size, total_tracks)
        percent = (progress / total_tracks) * 100
        sys.stdout.write(f"\r🚀 Progress: {progress:,} / {total_tracks:,} tracks ({percent:.1f}%)")
        sys.stdout.flush()

    print("\n\nStep 5: Cleaning up temporary workspace...")
    cursor.execute("DROP TABLE tmp_track_counts;")
    
    print("Step 6: Building final lookup indexes...")
    cursor.execute("CREATE INDEX idx_bi_seed_track ON bi_track_similarities(seed_track_id);")
    
    conn.commit()
    conn.close()
    print("Success!")

if __name__ == "__main__":
    if os.path.exists(DB_PATH):
        build_bi_summary_tables()
    else:
        print(f"Error: Database not found at {DB_PATH}.")