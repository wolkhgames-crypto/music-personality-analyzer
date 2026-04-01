import psycopg2

conn = psycopg2.connect(
    host="shinkansen.proxy.rlwy.net",
    port=48403,
    database="music_personality_db",
    user="postgres",
    password="QHAFImJPyIemSaqvrqYGTjwPOMzwhDRZ"
)

cur = conn.cursor()

print("=== Current state ===")
cur.execute("SELECT id, name FROM users ORDER BY id")
users = cur.fetchall()
print(f"Users: {len(users)}")
for user in users:
    print(f"  User {user[0]}: {user[1]}")

cur.execute("SELECT COUNT(*) FROM tracks")
print(f"Tracks: {cur.fetchone()[0]}")

print("\n=== Creating playlists for each user ===")

# Предположим что у каждого пользователя было по 20 треков (160 треков / 8 пользователей = 20)
tracks_per_user = 20

cur.execute("SELECT id FROM tracks ORDER BY id")
all_tracks = [row[0] for row in cur.fetchall()]

for i, user in enumerate(users):
    user_id = user[0]
    user_name = user[1]
    
    # Create playlist
    cur.execute(
        "INSERT INTO playlists (user_id, title, mood) VALUES (%s, %s, %s) RETURNING id",
        (user_id, f'Плейлист {user_name}', 'смешанный')
    )
    playlist_id = cur.fetchone()[0]
    print(f"Created playlist {playlist_id} for user {user_id} ({user_name})")
    
    # Link tracks (20 tracks per user)
    start_idx = i * tracks_per_user
    end_idx = start_idx + tracks_per_user
    user_tracks = all_tracks[start_idx:end_idx]
    
    for pos, track_id in enumerate(user_tracks, 1):
        cur.execute(
            "INSERT INTO playlist_tracks (playlist_id, track_id, position) VALUES (%s, %s, %s)",
            (playlist_id, track_id, pos)
        )
    
    print(f"  Linked {len(user_tracks)} tracks")

conn.commit()

print("\n=== Final state ===")
cur.execute("SELECT COUNT(*) FROM playlists")
print(f"Playlists: {cur.fetchone()[0]}")

cur.execute("SELECT COUNT(*) FROM playlist_tracks")
print(f"Playlist_tracks: {cur.fetchone()[0]}")

cur.close()
conn.close()

print("\nDone! Now run: python import_track_templates.py")
