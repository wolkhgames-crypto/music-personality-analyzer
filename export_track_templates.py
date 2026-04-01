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

print("Exporting track_templates...")
cur.execute("SELECT * FROM track_templates")
rows = cur.fetchall()

# Get column names
cur.execute("""
    SELECT column_name 
    FROM information_schema.columns 
    WHERE table_name = 'track_templates'
    ORDER BY ordinal_position
""")
columns = [row[0] for row in cur.fetchall()]

print(f"Columns: {columns}")
print(f"Total rows: {len(rows)}")

# Save to JSON
data = []
for row in rows:
    record = {}
    for i, col in enumerate(columns):
        value = row[i]
        # Convert Decimal to float
        if hasattr(value, '__float__'):
            value = float(value)
        # Convert datetime to string
        elif hasattr(value, 'isoformat'):
            value = value.isoformat()
        record[col] = value
    data.append(record)

with open('track_templates_backup.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"✓ Exported {len(data)} records to track_templates_backup.json")

cur.close()
conn.close()
