import psycopg2

conn = psycopg2.connect(
    host="shinkansen.proxy.rlwy.net",
    port=48403,
    database="music_personality_db",
    user="postgres",
    password="QHAFImJPyIemSaqvrqYGTjwPOMzwhDRZ"
)

cur = conn.cursor()

print("=== FINAL DATABASE STATE ===\n")

# Counts
print("Table counts:")
tables = ['users', 'playlists', 'tracks', 'playlist_tracks', 'track_templates']
for table in tables:
    cur.execute(f"SELECT COUNT(*) FROM {table}")
    print(f"  {table}: {cur.fetchone()[0]}")

# User -> Playlist -> Tracks relationships
print("\nUser -> Playlist -> Tracks:")
cur.execute("""
    SELECT 
        u.id, u.name, u.age, u.gender,
        p.id as playlist_id, p.mood,
        COUNT(pt.track_id) as tracks_count
    FROM users u
    JOIN playlists p ON p.user_id = u.id
    LEFT JOIN playlist_tracks pt ON pt.playlist_id = p.id
    GROUP BY u.id, u.name, u.age, u.gender, p.id, p.mood
    ORDER BY u.id
""")

for row in cur.fetchall():
    print(f"  User {row[0]} ({row[1]}, {row[2]}, {row[3]}) -> Playlist {row[4]} ({row[5]}) -> {row[6]} tracks")

# ID matching
print("\nID matching check:")
cur.execute("""
    SELECT u.id, p.id, u.id = p.id as match
    FROM users u
    JOIN playlists p ON p.user_id = u.id
    ORDER BY u.id
""")

all_match = True
for row in cur.fetchall():
    status = "OK" if row[2] else "MISMATCH"
    print(f"  [{status}] User {row[0]} -> Playlist {row[1]}")
    if not row[2]:
        all_match = False

print(f"\nResult: {'All IDs match!' if all_match else 'Some IDs do not match!'}")

cur.close()
conn.close()
