import psycopg2
import json

conn = psycopg2.connect(
    host="shinkansen.proxy.rlwy.net",
    port=48403,
    database="music_personality_db",
    user="postgres",
    password="QHAFImJPyIemSaqvrqYGTjwPOMzwhDRZ"
)

cur = conn.cursor()

print("Loading track_templates from backup...")
with open('track_templates_backup.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"Loaded {len(data)} records")

# Clear existing data in track_templates (if any)
cur.execute("DELETE FROM track_templates")
print(f"Cleared existing track_templates")

# Insert data
print("Inserting records...")
inserted = 0
for record in data:
    try:
        cur.execute("""
            INSERT INTO track_templates (title, artist, genre, energy, valence)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (title, artist) DO NOTHING
        """, (
            record['title'],
            record['artist'],
            record['genre'],
            record['energy'],
            record['valence']
        ))
        inserted += 1
        if inserted % 500 == 0:
            print(f"  Inserted {inserted} records...")
    except Exception as e:
        print(f"Error inserting record: {record['title']} - {e}")

conn.commit()

print(f"\nDone! Inserted {inserted} records")

# Verify
cur.execute("SELECT COUNT(*) FROM track_templates")
count = cur.fetchone()[0]
print(f"Total records in track_templates: {count}")

cur.close()
conn.close()
