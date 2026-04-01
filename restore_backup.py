import psycopg2

# Read the backup file
try:
    with open('Бекап на 24.03.sql', 'r', encoding='utf-8') as f:
        sql_backup = f.read()
except UnicodeDecodeError:
    with open('Бекап на 24.03.sql', 'r', encoding='latin-1') as f:
        sql_backup = f.read()

conn = psycopg2.connect(
    host="shinkansen.proxy.rlwy.net",
    port=48403,
    database="music_personality_db",
    user="postgres",
    password="QHAFImJPyIemSaqvrqYGTjwPOMzwhDRZ"
)

cur = conn.cursor()

print("Restoring backup...")

# Split by statements and execute
statements = sql_backup.split(';')
executed = 0

for statement in statements:
    statement = statement.strip()
    if not statement:
        continue
    
    # Skip comments and SET commands
    if statement.startswith('--') or statement.startswith('/*'):
        continue
    if statement.upper().startswith('SET ') or statement.upper().startswith('SELECT pg_catalog'):
        continue
    
    try:
        cur.execute(statement)
        executed += 1
        if executed % 10 == 0:
            print(f"Executed {executed} statements...")
    except Exception as e:
        # Skip errors for CREATE DATABASE, DROP DATABASE, etc.
        if 'already exists' in str(e) or 'does not exist' in str(e) or 'cannot drop' in str(e):
            continue
        print(f"Warning: {e}")
        print(f"Statement: {statement[:100]}...")

conn.commit()

print(f"\nBackup restored! Executed {executed} statements")

# Verify
print("\n=== Verification ===")
cur.execute("SELECT COUNT(*) FROM users")
print(f"Users: {cur.fetchone()[0]}")

cur.execute("SELECT COUNT(*) FROM playlists")
print(f"Playlists: {cur.fetchone()[0]}")

cur.execute("SELECT COUNT(*) FROM tracks")
print(f"Tracks: {cur.fetchone()[0]}")

cur.execute("SELECT COUNT(*) FROM playlist_tracks")
print(f"Playlist_tracks: {cur.fetchone()[0]}")

cur.close()
conn.close()

print("\nNow run: python import_track_templates.py")
