import psycopg2

conn = psycopg2.connect(
    host="shinkansen.proxy.rlwy.net",
    port=48403,
    database="music_personality_db",
    user="postgres",
    password="QHAFImJPyIemSaqvrqYGTjwPOMzwhDRZ"
)

cur = conn.cursor()

print("=== Checking ID mismatches ===\n")

# Check users and playlists
cur.execute("""
    SELECT u.id as user_id, u.name, p.id as playlist_id, p.title
    FROM users u
    LEFT JOIN playlists p ON p.user_id = u.id
    ORDER BY u.id
""")

print("Users and their playlists:")
for row in cur.fetchall():
    print(f"  User {row[0]} ({row[1]}) -> Playlist {row[2]} ({row[3]})")

# Check if playlist IDs match user IDs
cur.execute("""
    SELECT COUNT(*) 
    FROM users u
    JOIN playlists p ON p.user_id = u.id
    WHERE u.id != p.id
""")
mismatches = cur.fetchone()[0]

print(f"\nID mismatches: {mismatches}")

if mismatches > 0:
    print("\n=== Fixing ID mismatches ===")
    
    # Delete existing playlists and playlist_tracks
    cur.execute("DELETE FROM playlist_tracks")
    print("Deleted playlist_tracks")
    
    cur.execute("DELETE FROM playlists")
    print("Deleted playlists")
    
    # Reset sequence
    cur.execute("SELECT setval('playlists_id_seq', 1, false)")
    print("Reset playlists_id_seq")
    
    # Recreate playlists with matching IDs
    cur.execute("SELECT id, name FROM users ORDER BY id")
    users = cur.fetchall()
    
    cur.execute("SELECT id FROM tracks ORDER BY id")
    all_tracks = [row[0] for row in cur.fetchall()]
    
    tracks_per_user = 20
    
    for i, user in enumerate(users):
        user_id = user[0]
        user_name = user[1]
        
        # Insert with specific ID
        cur.execute(
            "INSERT INTO playlists (id, user_id, title, mood) VALUES (%s, %s, %s, %s)",
            (user_id, user_id, f'Плейлист {user_name}', 'смешанный')
        )
        print(f"Created playlist {user_id} for user {user_id}")
        
        # Link tracks
        start_idx = i * tracks_per_user
        end_idx = start_idx + tracks_per_user
        user_tracks = all_tracks[start_idx:end_idx]
        
        for pos, track_id in enumerate(user_tracks, 1):
            cur.execute(
                "INSERT INTO playlist_tracks (playlist_id, track_id, position) VALUES (%s, %s, %s)",
                (user_id, track_id, pos)
            )
    
    # Update sequence to max ID
    cur.execute("SELECT setval('playlists_id_seq', (SELECT MAX(id) FROM playlists))")
    
    conn.commit()
    print("\n✓ Fixed!")

print("\n=== Final verification ===")
cur.execute("""
    SELECT u.id as user_id, u.name, p.id as playlist_id
    FROM users u
    JOIN playlists p ON p.user_id = u.id
    ORDER BY u.id
""")

print("Users and playlists (should match):")
for row in cur.fetchall():
    match = "✓" if row[0] == row[2] else "✗"
    print(f"  {match} User {row[0]} ({row[1]}) -> Playlist {row[2]}")

cur.close()
conn.close()
