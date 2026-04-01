import psycopg2

conn = psycopg2.connect(
    host="shinkansen.proxy.rlwy.net",
    port=48403,
    database="music_personality_db",
    user="postgres",
    password="QHAFImJPyIemSaqvrqYGTjwPOMzwhDRZ"
)

cur = conn.cursor()

# Показать все таблицы
print("=== All tables ===")
cur.execute("""
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema = 'public'
""")
for row in cur.fetchall():
    print(row[0])

# Показать количество записей в каждой таблице
print("\n=== Row counts ===")
tables = ['users', 'playlists', 'tracks', 'playlist_tracks', 'track_templates']
for table in tables:
    try:
        cur.execute(f"SELECT COUNT(*) FROM {table}")
        count = cur.fetchone()[0]
        print(f"{table}: {count}")
    except Exception as e:
        print(f"{table}: Error - {e}")

cur.close()
conn.close()
