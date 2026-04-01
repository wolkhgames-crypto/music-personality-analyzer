import psycopg2

conn = psycopg2.connect(
    host="shinkansen.proxy.rlwy.net",
    port=48403,
    database="music_personality_db",
    user="postgres",
    password="QHAFImJPyIemSaqvrqYGTjwPOMzwhDRZ"
)

cur = conn.cursor()

print("=== Current data count ===")
cur.execute("SELECT COUNT(*) FROM users")
print(f"Users: {cur.fetchone()[0]}")

cur.execute("SELECT COUNT(*) FROM playlists")
print(f"Playlists: {cur.fetchone()[0]}")

cur.execute("SELECT COUNT(*) FROM tracks")
print(f"Tracks: {cur.fetchone()[0]}")

cur.execute("SELECT COUNT(*) FROM playlist_tracks")
print(f"Playlist_tracks: {cur.fetchone()[0]}")

print("\n=== Deleting test data ===")

# Delete in correct order (foreign keys)
cur.execute("DELETE FROM playlist_tracks")
print(f"Deleted {cur.rowcount} playlist_tracks")

cur.execute("DELETE FROM playlists")
print(f"Deleted {cur.rowcount} playlists")

cur.execute("DELETE FROM tracks")
print(f"Deleted {cur.rowcount} tracks")

cur.execute("DELETE FROM users")
print(f"Deleted {cur.rowcount} users")

conn.commit()

print("\n=== Data count after cleanup ===")
cur.execute("SELECT COUNT(*) FROM users")
print(f"Users: {cur.fetchone()[0]}")

cur.execute("SELECT COUNT(*) FROM playlists")
print(f"Playlists: {cur.fetchone()[0]}")

cur.execute("SELECT COUNT(*) FROM tracks")
print(f"Tracks: {cur.fetchone()[0]}")

cur.execute("SELECT COUNT(*) FROM playlist_tracks")
print(f"Playlist_tracks: {cur.fetchone()[0]}")

print("\n✅ Database cleaned!")

cur.close()
conn.close()
