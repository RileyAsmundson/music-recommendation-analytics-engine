import sqlite3
import os
import sys

DB_PATH = "data/processed/vibe_warehouse.db"

def optimize_for_powerbi_batched():
    print("Connecting to database...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Enable fast reading/writing
    cursor.execute("PRAGMA journal_mode = WAL;")
    cursor.execute("PRAGMA synchronous = OFF;")
    
    # Optional: Increase cache size to keep more operations in RAM
    cursor.execute("PRAGMA cache_size = -64000;") 

    print("Step 1: Initializing the hybrid table...")
    cursor.execute("DROP TABLE IF EXISTS bi_track_similarities_hybrid;")
    cursor.execute("""
        CREATE TABLE bi_track_similarities_hybrid (
            seed_track_id INTEGER,
            match_track_id INTEGER,
            jaccard_score REAL,
            rec_type TEXT
        );
    """)

    print("Step 2: Fetching all unique seed tracks...")
    cursor.execute("SELECT DISTINCT seed_track_id FROM bi_track_similarities;")
    seed_tracks = [row[0] for row in cursor.fetchall()]
    total_tracks = len(seed_tracks)
    print(f"-> Found {total_tracks:,} tracks to categorize.")

    print("Step 3: Commencing fast-batch categorization (Top 3 Same / Top 3 Cross)...")
    batch_size = 1000
    
    for i in range(0, total_tracks, batch_size):
        batch = seed_tracks[i:i + batch_size]
        placeholders = ','.join(['?'] * len(batch))
        
        # Process only the current batch of tracks
        cursor.execute(f"""
            INSERT INTO bi_track_similarities_hybrid (seed_track_id, match_track_id, jaccard_score, rec_type)
            WITH CategorizedMatches AS (
                SELECT 
                    s.seed_track_id,
                    s.match_track_id,
                    s.jaccard_score,
                    CASE 
                        WHEN t_seed.artist_name = t_match.artist_name THEN 'Same Artist' 
                        ELSE 'Cross Artist' 
                    END AS rec_type,
                    ROW_NUMBER() OVER (
                        PARTITION BY s.seed_track_id, 
                                     (CASE WHEN t_seed.artist_name = t_match.artist_name THEN 1 ELSE 0 END)
                        ORDER BY s.jaccard_score DESC
                    ) AS category_rank
                FROM bi_track_similarities s
                JOIN tracks t_seed ON s.seed_track_id = t_seed.track_id
                JOIN tracks t_match ON s.match_track_id = t_match.track_id
                WHERE s.seed_track_id IN ({placeholders})
            )
            SELECT 
                seed_track_id,
                match_track_id,
                jaccard_score,
                rec_type
            FROM CategorizedMatches
            WHERE category_rank <= 3;
        """, batch)
        
        # Commit this batch to disk
        conn.commit()
        
        # Update progress bar
        progress = min(i + batch_size, total_tracks)
        percent = (progress / total_tracks) * 100
        sys.stdout.write(f"Progress: {progress:,} / {total_tracks:,} tracks ({percent:.1f}%)")
        sys.stdout.flush()

    print("\n\nStep 4: Creating the optimized tracks dimension table (no orphans)...")
    cursor.execute("DROP TABLE IF EXISTS bi_tracks;")
    cursor.execute("""
        CREATE TABLE bi_tracks AS
        SELECT * 
        FROM tracks
        WHERE track_id IN (SELECT DISTINCT seed_track_id FROM bi_track_similarities_hybrid);
    """)

    print("Step 5: Building indexes for lightning-fast Power BI performance...")
    cursor.execute("CREATE INDEX idx_hybrid_seed ON bi_track_similarities_hybrid(seed_track_id);")
    cursor.execute("CREATE INDEX idx_bi_tracks_id ON bi_tracks(track_id);")

    conn.commit()
    conn.close()
    print("Success.")

if __name__ == "__main__":
    if os.path.exists(DB_PATH):
        optimize_for_powerbi_batched()
    else:
        print(f"Error: Database not found at {DB_PATH}.")