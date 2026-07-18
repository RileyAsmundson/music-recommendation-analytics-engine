import sqlite3

DB_PATH = "data/processed/vibe_warehouse.db"
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

print("Checking data warehouse...")
print("-" * 40)

# List of tables to check
tables = ['users', 'tracks', 'playlists', 'playlist_tracks']

for table in tables:
    cursor.execute(f"SELECT COUNT(*) FROM {table}")
    count = cursor.fetchone()[0]
    print(f"Table '{table}': {count:,} rows")

print("-" * 40)
print("🎵 Quick Sample from TRACKS Table:")
cursor.execute("SELECT * FROM tracks LIMIT 5")
for row in cursor.fetchall():
    print(f"   ID {row[0]}: {row[1]} - {row[2]}")

conn.close()