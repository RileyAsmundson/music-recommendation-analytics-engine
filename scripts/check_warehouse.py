import sqlite3
import pandas as pd

DB_PATH = "data/processed/vibe_warehouse.db"
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

print("Checking data warehouse...")
print("-" * 40)

tables = ['users', 'tracks', 'playlists', 'playlist_tracks']

# --- 1. Row Counts ---
# (We still use raw SQL for this because asking Pandas to load 12.8M rows just to count them would crash your memory!)
for table in tables:
    cursor.execute(f"SELECT COUNT(*) FROM {table}")
    count = cursor.fetchone()[0]
    print(f"Table '{table}': {count:,} rows")

print("-" * 40)

# --- 2. Pandas Tabular View ---
for table in tables:
    print(f"\nQuick Sample from {table.upper()} Table:")
    print("\n")
    
    # Pass the SQL query and the connection directly to Pandas
    df = pd.read_sql_query(f"SELECT * FROM {table} LIMIT 5", conn)
    
    # Print the DataFrame as a string (hiding the default pandas index numbers for a cleaner look)
    print(df.to_string(index=False))

print("\n" + "-" * 40)
print("Database check complete.")

conn.close()