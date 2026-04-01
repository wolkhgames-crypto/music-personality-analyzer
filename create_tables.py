import psycopg2

# Database configuration
DB_CONFIG = {
    'host': 'shinkansen.proxy.rlwy.net',
    'port': 48403,
    'database': 'railway',
    'user': 'postgres',
    'password': 'QHAFImJPyIemSaqvrqYGTjwPOMzwhDRZ'
}

print("Connecting to database...")
conn = psycopg2.connect(**DB_CONFIG)
cur = conn.cursor()

print("Creating tables...")

# Create tables
cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    id      SERIAL PRIMARY KEY,
    name    VARCHAR(100) NOT NULL,
    age     INT,
    gender  VARCHAR(20)
);
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS tracks (
    id      SERIAL PRIMARY KEY,
    title   VARCHAR(200) NOT NULL,
    artist  VARCHAR(100),
    genre   VARCHAR(100),
    energy  FLOAT CHECK (energy BETWEEN 0 AND 1),
    valence FLOAT CHECK (valence BETWEEN 0 AND 1)
);
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS playlists (
    id      SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id) ON DELETE CASCADE,
    title   VARCHAR(200) NOT NULL,
    mood    VARCHAR(100)
);
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS playlist_tracks (
    playlist_id INT REFERENCES playlists(id) ON DELETE CASCADE,
    track_id    INT REFERENCES tracks(id) ON DELETE CASCADE,
    position    INT,
    PRIMARY KEY (playlist_id, track_id)
);
""")

conn.commit()
print("Tables created successfully!")

# Check tables
cur.execute("""
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public'
ORDER BY table_name;
""")

tables = cur.fetchall()
print(f"\nTables in database: {[t[0] for t in tables]}")

cur.close()
conn.close()
print("\nDone!")
