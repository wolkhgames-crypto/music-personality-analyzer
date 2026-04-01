import psycopg2

conn = psycopg2.connect(
    host="shinkansen.proxy.rlwy.net",
    port=48403,
    database="music_personality_db",
    user="postgres",
    password="QHAFImJPyIemSaqvrqYGTjwPOMzwhDRZ"
)

cur = conn.cursor()

print("=== USERS ===")
cur.execute("SELECT * FROM users ORDER BY id DESC LIMIT 5;")
for row in cur.fetchall():
    print(row)

print("\n=== PLAYLISTS ===")
cur.execute("SELECT * FROM playlists ORDER BY id DESC LIMIT 5;")
for row in cur.fetchall():
    print(row)

print("\n=== TRACKS ===")
cur.execute("SELECT id, artist, title, energy, valence FROM tracks ORDER BY id DESC LIMIT 5;")
for row in cur.fetchall():
    print(row)

print("\n=== PLAYLIST_TRACKS ===")
cur.execute("SELECT * FROM playlist_tracks LIMIT 5;")
for row in cur.fetchall():
    print(row)

print("\n=== JOIN TEST ===")
cur.execute("""
    SELECT u.id, u.name, COUNT(t.id) as track_count 
    FROM users u 
    LEFT JOIN playlists pl ON pl.user_id = u.id 
    LEFT JOIN playlist_tracks pt ON pt.playlist_id = pl.id 
    LEFT JOIN tracks t ON t.id = pt.track_id 
    GROUP BY u.id, u.name;
""")
for row in cur.fetchall():
    print(row)

cur.close()
conn.close()
