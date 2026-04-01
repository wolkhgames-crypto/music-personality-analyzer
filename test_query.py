import psycopg2

conn = psycopg2.connect(
    host="shinkansen.proxy.rlwy.net",
    port=48403,
    database="music_personality_db",
    user="postgres",
    password="QHAFImJPyIemSaqvrqYGTjwPOMzwhDRZ"
)

cur = conn.cursor()

# Тестируем с последним пользователем (id=44)
user_id = 44

query = """
SELECT
    u.name,
    u.age,
    u.gender,
    ROUND(COUNT(*) FILTER (WHERE t.energy >= 0.65 AND t.valence >= 0.6) * 1.0 / COUNT(*), 2) AS hype_ratio,
    ROUND(COUNT(*) FILTER (WHERE t.energy >= 0.65 AND t.valence < 0.4) * 1.0 / COUNT(*), 2) AS aggressive_ratio,
    ROUND(COUNT(*) FILTER (WHERE t.energy < 0.65 AND t.valence < 0.4) * 1.0 / COUNT(*), 2) AS sad_ratio,
    ROUND(COUNT(*) FILTER (WHERE t.energy < 0.65 AND t.valence >= 0.55) * 1.0 / COUNT(*), 2) AS calm_ratio,
    CASE
        WHEN COALESCE(STDDEV(t.valence), 0) < 0.15 AND AVG(t.valence) > 0.6 
            THEN 'Стабильно-позитивный'
        WHEN COALESCE(STDDEV(t.valence), 0) < 0.15 AND AVG(t.valence) < 0.4 
            THEN 'Стабильно-негативный'
        WHEN COUNT(*) FILTER (WHERE t.energy >= 0.65 AND t.valence >= 0.6) > COUNT(*) * 0.25
            THEN 'Эйфорический'
        WHEN COUNT(*) FILTER (WHERE t.energy >= 0.65 AND t.valence < 0.4) > COUNT(*) * 0.25
            THEN 'Тревожно-агрессивный'
        WHEN COUNT(*) FILTER (WHERE t.energy < 0.65 AND t.valence < 0.4) > COUNT(*) * 0.25
            THEN 'Меланхолический'
        WHEN COUNT(*) FILTER (WHERE t.energy < 0.65 AND t.valence >= 0.55) > COUNT(*) * 0.25
            THEN 'Спокойно-оптимистичный'
        WHEN COUNT(*) FILTER (WHERE t.energy >= 0.65 AND t.valence < 0.4) > COUNT(*) * 0.15
         AND COUNT(*) FILTER (WHERE t.energy < 0.65 AND t.valence < 0.4) > COUNT(*) * 0.15
            THEN 'Депрессивно-агрессивный'
        WHEN COUNT(*) FILTER (WHERE t.energy >= 0.65 AND t.valence >= 0.6) > COUNT(*) * 0.15
         AND COUNT(*) FILTER (WHERE t.energy < 0.65 AND t.valence >= 0.55) > COUNT(*) * 0.15
            THEN 'Позитивно-уравновешенный'
        WHEN COUNT(*) FILTER (WHERE t.energy >= 0.65) > COUNT(*) * 0.50
            THEN 'Высокоэнергичный'
        WHEN COUNT(*) FILTER (WHERE t.valence < 0.4) > COUNT(*) * 0.50
            THEN 'Преимущественно-негативный'
        WHEN COUNT(*) FILTER (WHERE t.valence >= 0.6) > COUNT(*) * 0.50
            THEN 'Преимущественно-позитивный'
        WHEN COALESCE(STDDEV(t.valence), 0) > 0.25 OR COALESCE(STDDEV(t.energy), 0) > 0.25
            THEN 'Эмоционально-нестабильный'
        ELSE 'Сбалансированный'
    END AS personality_type
FROM users u
JOIN playlists pl       ON pl.user_id = u.id
JOIN playlist_tracks pt ON pt.playlist_id = pl.id
JOIN tracks t           ON t.id = pt.track_id
WHERE u.id = %s
GROUP BY u.name, u.age, u.gender;
"""

print(f"Testing query for user_id={user_id}")
cur.execute(query, (user_id,))
result = cur.fetchone()

print(f"\nResult: {result}")

if result:
    print(f"\nName: {result[0]}")
    print(f"Age: {result[1]}")
    print(f"Gender: {result[2]}")
    print(f"Hype ratio: {result[3]}")
    print(f"Aggressive ratio: {result[4]}")
    print(f"Sad ratio: {result[5]}")
    print(f"Calm ratio: {result[6]}")
    print(f"Personality: {result[7]}")
else:
    print("No result returned!")

cur.close()
conn.close()
