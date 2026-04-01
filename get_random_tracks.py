import psycopg2

conn = psycopg2.connect(
    host="shinkansen.proxy.rlwy.net",
    port=48403,
    database="music_personality_db",
    user="postgres",
    password="QHAFImJPyIemSaqvrqYGTjwPOMzwhDRZ"
)

cur = conn.cursor()

# Get random tracks from track_templates
print("=== Random tracks from track_templates ===")
cur.execute("""
    SELECT title, artist, genre, energy, valence 
    FROM track_templates 
    ORDER BY RANDOM() 
    LIMIT 10
""")

for row in cur.fetchall():
    print(f"{row[0]} - {row[1]} (genre: {row[2]}, energy: {row[3]}, valence: {row[4]})")

cur.close()
conn.close()
