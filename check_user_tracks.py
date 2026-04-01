import psycopg2

conn = psycopg2.connect(
    host="shinkansen.proxy.rlwy.net",
    port=48403,
    database="music_personality_db",
    user="postgres",
    password="QHAFImJPyIemSaqvrqYGTjwPOMzwhDRZ"
)

cur = conn.cursor()

# Проверяем последнего пользователя (id=44)
user_id = 44

print(f"=== Checking user_id={user_id} ===\n")

print("User info:")
cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
print(cur.fetchone())

print("\nPlaylist info:")
cur.execute("SELECT * FROM playlists WHERE user_id = %s", (user_id,))
print(cur.fetchone())

print("\nPlaylist tracks:")
cur.execute("""
    SELECT pt.playlist_id, pt.track_id, pt.position 
    FROM playlist_tracks pt
    JOIN playlists pl ON pl.id = pt.playlist_id
    WHERE pl.user_id = %s
""", (user_id,))
for row in cur.fetchall():
    print(row)

print("\nTracks for this user:")
cur.execute("""
    SELECT t.id, t.title, t.artist, t.energy, t.valence
    FROM tracks t
    JOIN playlist_tracks pt ON pt.track_id = t.id
    JOIN playlists pl ON pl.id = pt.playlist_id
    WHERE pl.user_id = %s
""", (user_id,))
for row in cur.fetchall():
    print(row)

cur.close()
conn.close()
