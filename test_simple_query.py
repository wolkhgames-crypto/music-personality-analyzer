import psycopg2

conn = psycopg2.connect(
    host="shinkansen.proxy.rlwy.net",
    port=48403,
    database="music_personality_db",
    user="postgres",
    password="QHAFImJPyIemSaqvrqYGTjwPOMzwhDRZ"
)

cur = conn.cursor()

user_id = 44

# Простой запрос сначала
print("=== Simple query ===")
cur.execute("""
    SELECT u.name, u.age, u.gender, COUNT(t.id) as track_count
    FROM users u
    JOIN playlists pl ON pl.user_id = u.id
    JOIN playlist_tracks pt ON pt.playlist_id = pl.id
    JOIN tracks t ON t.id = pt.track_id
    WHERE u.id = %s
    GROUP BY u.name, u.age, u.gender
""", (user_id,))
result = cur.fetchone()
print(f"Result: {result}")

# Теперь с ROUND и FILTER
print("\n=== With ROUND and FILTER ===")
cur.execute("""
    SELECT
        u.name,
        u.age,
        u.gender,
        ROUND(COUNT(*) FILTER (WHERE t.energy >= 0.65 AND t.valence >= 0.6) * 1.0 / COUNT(*), 2) AS hype_ratio
    FROM users u
    JOIN playlists pl ON pl.user_id = u.id
    JOIN playlist_tracks pt ON pt.playlist_id = pl.id
    JOIN tracks t ON t.id = pt.track_id
    WHERE u.id = %s
    GROUP BY u.name, u.age, u.gender
""", (user_id,))
result = cur.fetchone()
print(f"Result: {result}")

cur.close()
conn.close()
