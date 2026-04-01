import psycopg2

conn = psycopg2.connect(
    host="shinkansen.proxy.rlwy.net",
    port=48403,
    database="music_personality_db",
    user="postgres",
    password="QHAFImJPyIemSaqvrqYGTjwPOMzwhDRZ"
)

cur = conn.cursor()

print("=== Verification ===\n")

cur.execute("""
    SELECT u.id as user_id, u.name, p.id as playlist_id, p.title
    FROM users u
    JOIN playlists p ON p.user_id = u.id
    ORDER BY u.id
""")

print("Users and playlists:")
all_match = True
for row in cur.fetchall():
    match = row[0] == row[2]
    symbol = "OK" if match else "MISMATCH"
    print(f"  [{symbol}] User {row[0]} -> Playlist {row[2]}")
    if not match:
        all_match = False

if all_match:
    print("\nAll IDs match! Database fully restored.")
else:
    print("\nSome IDs still don't match!")

cur.close()
conn.close()
