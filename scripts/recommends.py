import sqlite3

DB_PATH = "data/processed/vibe_warehouse.db"

def parse_search_term(search_term):
    """Splits input into song and artist if 'by' or '-' is present."""
    term = search_term.strip()
    if " by " in term.lower():
        parts = term.lower().split(" by ", 1)
        return parts[0].strip(), parts[1].strip()
    elif " - " in term:
        parts = term.lower().split(" - ", 1)
        return parts[0].strip(), parts[1].strip()
    return term.lower(), None

def search_track(search_term):
    """Searches for tracks, de-duplicates them, and ranks them by global popularity."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    song, artist = parse_search_term(search_term)
    
    if artist:
        query = """
            SELECT MIN(t.track_id), t.artist_name, t.track_name, COUNT(pt.playlist_id) as popularity
            FROM tracks t
            INNER JOIN playlist_tracks pt ON t.track_id = pt.track_id
            WHERE LOWER(t.track_name) LIKE ? AND LOWER(t.artist_name) LIKE ?
            GROUP BY LOWER(t.artist_name), LOWER(t.track_name)
            ORDER BY popularity DESC
            LIMIT 5;
        """
        cursor.execute(query, (f"%{song}%", f"%{artist}%"))
    else:
        query = """
            SELECT MIN(t.track_id), t.artist_name, t.track_name, COUNT(pt.playlist_id) as popularity
            FROM tracks t
            INNER JOIN playlist_tracks pt ON t.track_id = pt.track_id
            WHERE LOWER(t.track_name) LIKE ? OR LOWER(t.artist_name) LIKE ?
            GROUP BY LOWER(t.artist_name), LOWER(t.track_name)
            ORDER BY popularity DESC
            LIMIT 5;
        """
        cursor.execute(query, (f"%{song}%", f"%{song}%"))
        
    results = cursor.fetchall()
    conn.close()
    return results

def get_all_variant_ids(artist_name, track_name):
    """Finds all unique track_ids that belong to this song regardless of casing."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    query = """
        SELECT track_id FROM tracks 
        WHERE LOWER(artist_name) = LOWER(?) AND LOWER(track_name) = LOWER(?);
    """
    cursor.execute(query, (artist_name, track_name))
    ids = [row[0] for row in cursor.fetchall()]
    conn.close()
    return ids

def get_jaccard_recommendations(track_ids, seed_artist, min_cooccurrence=3):
    """
    Core Recommendation Engine.
    Uses Jaccard Similarity to eliminate popularity bias, returning both cross-artist and same-artist results.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    id_placeholders = ", ".join(["?"] * len(track_ids))
    
    # 1. Get all unique playlists containing our seed track variants (Set A)
    cursor.execute(f"SELECT DISTINCT playlist_id FROM playlist_tracks WHERE track_id IN ({id_placeholders})", track_ids)
    seed_playlists = set(row[0] for row in cursor.fetchall())
    total_seed_playlists = len(seed_playlists)
    
    if total_seed_playlists == 0:
        conn.close()
        return [], []

    # 2. Find candidates that share playlists, applying a noise filter (min_cooccurrence)
    query = f"""
        SELECT pt.track_id, COUNT(pt.playlist_id) as shared_count, t.artist_name, t.track_name
        FROM playlist_tracks pt
        JOIN tracks t ON pt.track_id = t.track_id
        WHERE pt.playlist_id IN (
            SELECT playlist_id FROM playlist_tracks WHERE track_id IN ({id_placeholders})
        )
        AND pt.track_id NOT IN ({id_placeholders})
        GROUP BY pt.track_id
        HAVING shared_count >= ?
    """
    params = track_ids + track_ids + [min_cooccurrence]
    cursor.execute(query, params)
    candidates = cursor.fetchall()
    
    cross_recs = []
    same_recs = []
    
    # 3. Calculate Jaccard Similarity for each candidate
    for candidate_id, shared_count, artist_name, track_name in candidates:
        # Get total playlist count for the candidate track (Set B)
        cursor.execute("SELECT COUNT(playlist_id) FROM playlist_tracks WHERE track_id = ?", (candidate_id,))
        total_candidate_playlists = cursor.fetchone()[0]
        
        # Jaccard Formula: Intersection / (Set A + Set B - Intersection)
        union = total_seed_playlists + total_candidate_playlists - shared_count
        jaccard_score = shared_count / union if union > 0 else 0
        
        # Multiply by 100 for a cleaner "Match Score" display
        match_percentage = round(jaccard_score * 100, 2)
        rec_data = (artist_name.title(), track_name.title(), match_percentage, shared_count)
        
        # Route to the appropriate engine array
        if artist_name.lower() == seed_artist.lower():
            same_recs.append(rec_data)
        else:
            cross_recs.append(rec_data)
            
    conn.close()
    
    # Sort both lists by the Jaccard Score (highest first)
    cross_recs = sorted(cross_recs, key=lambda x: x[2], reverse=True)
    same_recs = sorted(same_recs, key=lambda x: x[2], reverse=True)
    
    return cross_recs, same_recs

def main():
    print("Dual-Engine Vibe Recommendation System (Jaccard Anti-Bias)")
    print("=" * 60)
    
    keyword = input("Search (e.g., 'Stay the night'): ").strip()
    if not keyword:
        return
        
    matches = search_track(keyword)
    if not matches:
        print("No matches found in the warehouse.")
        return
        
    print("\nMatches found:")
    for idx, match in enumerate(matches):
        print(f"  [{idx + 1}] {match[1].title()} - {match[2].title()}")
        
    try:
        selection = int(input("\nSelect your track number: ")) - 1
        if selection < 0 or selection >= len(matches):
            return
    except ValueError:
        return
        
    chosen_artist = matches[selection][1]
    chosen_track = matches[selection][2]
    
    all_ids = get_all_variant_ids(chosen_artist, chosen_track)
    
    print(f"\nMerging data across {len(all_ids)} casing variants...")
    print(f"Calculating Jaccard Matrix for: '{chosen_artist.title()} - {chosen_track.title()}'...\n")
    
    # Run the algorithm and grab the top 5 from both categories
    cross_recs, same_recs = get_jaccard_recommendations(all_ids, chosen_artist, min_cooccurrence=3)
    cross_top_5 = cross_recs[:5]
    same_top_5 = same_recs[:5]
    
    # --- SECTION 1: SIMILAR VIBES (DIFFERENT ARTISTS) ---
    print("SECTION 1: SIMILAR VIBES (CROSS-ARTIST DISCOVERY)")
    print("-" * 60)
    if not cross_top_5:
        print("  No cross-artist recommendations found. (Try a less obscure track)")
    else:
        for rank, (artist, track, score, shared) in enumerate(cross_top_5, 1):
            print(f"  {rank}. {artist} - {track}")
            print(f"     Match Score: {score}%")
            
    print("\n")
    
    # --- SECTION 2: MORE BY THIS ARTIST ---
    print(f"SECTION 2: MORE BY {chosen_artist.upper()} (VIBE-ALIGNED)")
    print("-" * 60)
    if not same_top_5:
        print(f"  No other tracks found in matching playlists.")
    else:
        for rank, (artist, track, score, shared) in enumerate(same_top_5, 1):
            print(f"  {rank}. {track}")
            print(f"     Match Score: {score}%")
    print("-" * 60)

if __name__ == "__main__":
    main()