-- ============================================
-- SQL-запросы для конференции
-- Тема: "Музыкальный плейлист как отражение личности"
-- ============================================

-- ============================================
-- 1. СОЗДАНИЕ СТРУКТУРЫ БД
-- ============================================

-- Создание базы данных
CREATE DATABASE music_personality_db;

-- Подключение к БД
\c music_personality_db;

-- Таблица пользователей
CREATE TABLE users (
    id      SERIAL PRIMARY KEY,
    name    VARCHAR(100) NOT NULL,
    age     INT,
    gender  VARCHAR(20)
);

-- Таблица треков с характеристиками
CREATE TABLE tracks (
    id      SERIAL PRIMARY KEY,
    title   VARCHAR(200) NOT NULL,
    artist  VARCHAR(100),
    genre   VARCHAR(100),
    energy  FLOAT CHECK (energy BETWEEN 0 AND 1),
    valence FLOAT CHECK (valence BETWEEN 0 AND 1)
);

-- Таблица плейлистов
CREATE TABLE playlists (
    id      SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id) ON DELETE CASCADE,
    title   VARCHAR(200) NOT NULL,
    mood    VARCHAR(100)
);

-- Связующая таблица (многие-ко-многим)
CREATE TABLE playlist_tracks (
    playlist_id INT REFERENCES playlists(id) ON DELETE CASCADE,
    track_id    INT REFERENCES tracks(id) ON DELETE CASCADE,
    position    INT,
    PRIMARY KEY (playlist_id, track_id)
);

-- ============================================
-- 2. ПРОСМОТР ДАННЫХ
-- ============================================

-- Все пользователи
SELECT * FROM users;

-- Примеры треков с характеристиками
SELECT id, title, artist, energy, valence 
FROM tracks 
LIMIT 10;

-- Плейлисты пользователей
SELECT u.name, pl.title, pl.mood
FROM users u
JOIN playlists pl ON pl.user_id = u.id;

-- Треки конкретного пользователя
SELECT u.name, t.title, t.artist, t.energy, t.valence
FROM users u
JOIN playlists pl ON pl.user_id = u.id
JOIN playlist_tracks pt ON pt.playlist_id = pl.id
JOIN tracks t ON t.id = pt.track_id
WHERE u.id = 1
ORDER BY pt.position;

-- ============================================
-- 3. АНАЛИЗ ЛИЧНОСТИ - ВСЕ УЧАСТНИКИ
-- ============================================

SELECT
    u.name,
    u.age,
    u.gender,
    ROUND(COUNT(*) FILTER (WHERE t.energy >= 0.65 AND t.valence >= 0.6) * 1.0 / COUNT(*), 2) AS hype_ratio,
    ROUND(COUNT(*) FILTER (WHERE t.energy >= 0.65 AND t.valence < 0.4) * 1.0 / COUNT(*), 2) AS aggressive_ratio,
    ROUND(COUNT(*) FILTER (WHERE t.energy < 0.65 AND t.valence < 0.4) * 1.0 / COUNT(*), 2) AS sad_ratio,
    ROUND(COUNT(*) FILTER (WHERE t.energy < 0.65 AND t.valence >= 0.55) * 1.0 / COUNT(*), 2) AS calm_ratio,
    CASE
        WHEN COUNT(*) FILTER (WHERE t.energy >= 0.65 AND t.valence >= 0.6) > COUNT(*) * 0.30
            THEN 'Эйфорический экстраверт'
        WHEN COUNT(*) FILTER (WHERE t.energy >= 0.65 AND t.valence < 0.4) > COUNT(*) * 0.30
            THEN 'Тревожный активист'
        WHEN COUNT(*) FILTER (WHERE t.energy < 0.65 AND t.valence < 0.4) > COUNT(*) * 0.30
            THEN 'Меланхолик'
        WHEN COUNT(*) FILTER (WHERE t.energy < 0.65 AND t.valence >= 0.55) > COUNT(*) * 0.30
            THEN 'Созерцательный оптимист'
        WHEN COUNT(*) FILTER (WHERE t.energy >= 0.65 AND t.valence < 0.4) > COUNT(*) * 0.20
         AND COUNT(*) FILTER (WHERE t.energy < 0.65 AND t.valence < 0.4) > COUNT(*) * 0.20
            THEN 'Меланхолик с агрессией'
        WHEN COUNT(*) FILTER (WHERE t.energy >= 0.65 AND t.valence >= 0.6) > COUNT(*) * 0.20
         AND COUNT(*) FILTER (WHERE t.energy < 0.65 AND t.valence >= 0.55) > COUNT(*) * 0.20
            THEN 'Позитивный микс'
        ELSE 'Эмоционально нестабильный'
    END AS personality_type
FROM users u
JOIN playlists pl       ON pl.user_id = u.id
JOIN playlist_tracks pt ON pt.playlist_id = pl.id
JOIN tracks t           ON t.id = pt.track_id
GROUP BY u.name, u.age, u.gender;

-- ============================================
-- 4. АНАЛИЗ КОНКРЕТНОГО УЧАСТНИКА
-- ============================================

SELECT
    u.name,
    u.age,
    u.gender,
    ROUND(COUNT(*) FILTER (WHERE t.energy >= 0.6 AND t.valence >= 0.6) * 1.0 / COUNT(*), 2) AS hype_ratio,
    ROUND(COUNT(*) FILTER (WHERE t.energy >= 0.6 AND t.valence < 0.45) * 1.0 / COUNT(*), 2) AS aggressive_ratio,
    ROUND(COUNT(*) FILTER (WHERE t.energy < 0.5  AND t.valence < 0.45) * 1.0 / COUNT(*), 2) AS sad_ratio,
    ROUND(COUNT(*) FILTER (WHERE t.energy < 0.5  AND t.valence >= 0.6) * 1.0 / COUNT(*), 2) AS calm_ratio,
    CASE
        WHEN COUNT(*) FILTER (WHERE t.energy >= 0.6 AND t.valence >= 0.6) > COUNT(*) * 0.30
            THEN 'Эйфорический экстраверт'
        WHEN COUNT(*) FILTER (WHERE t.energy >= 0.6 AND t.valence < 0.45) > COUNT(*) * 0.30
            THEN 'Тревожный активист'
        WHEN COUNT(*) FILTER (WHERE t.energy < 0.5  AND t.valence < 0.45) > COUNT(*) * 0.30
            THEN 'Меланхолик'
        WHEN COUNT(*) FILTER (WHERE t.energy < 0.5  AND t.valence >= 0.6) > COUNT(*) * 0.30
            THEN 'Созерцательный оптимист'
        WHEN COUNT(*) FILTER (WHERE t.energy >= 0.6 AND t.valence < 0.45) > COUNT(*) * 0.20
         AND COUNT(*) FILTER (WHERE t.energy < 0.5  AND t.valence < 0.45) > COUNT(*) * 0.20
            THEN 'Меланхолик с агрессией'
        WHEN COUNT(*) FILTER (WHERE t.energy >= 0.6 AND t.valence >= 0.6) > COUNT(*) * 0.20
         AND COUNT(*) FILTER (WHERE t.energy < 0.5  AND t.valence >= 0.6) > COUNT(*) * 0.20
            THEN 'Позитивный микс'
        ELSE 'Эмоционально нестабильный'
    END AS personality_type
FROM users u
JOIN playlists pl       ON pl.user_id = u.id
JOIN playlist_tracks pt ON pt.playlist_id = pl.id
JOIN tracks t           ON t.id = pt.track_id
WHERE u.id = 1  -- Меняй на нужного участника
GROUP BY u.name, u.age, u.gender;

-- ============================================
-- 5. СТАТИСТИКА ПО БАЗЕ
-- ============================================

-- Общее количество данных
SELECT 
    (SELECT COUNT(*) FROM users) AS total_users,
    (SELECT COUNT(*) FROM tracks) AS total_tracks,
    (SELECT COUNT(*) FROM playlists) AS total_playlists;

-- Средние значения по всем трекам
SELECT 
    ROUND(AVG(energy)::numeric, 2) AS avg_energy,
    ROUND(AVG(valence)::numeric, 2) AS avg_valence,
    ROUND(MIN(energy)::numeric, 2) AS min_energy,
    ROUND(MAX(energy)::numeric, 2) AS max_energy,
    ROUND(MIN(valence)::numeric, 2) AS min_valence,
    ROUND(MAX(valence)::numeric, 2) AS max_valence
FROM tracks;

-- Распределение по жанрам
SELECT genre, COUNT(*) as count
FROM tracks
WHERE genre IS NOT NULL
GROUP BY genre
ORDER BY count DESC
LIMIT 10;

-- Распределение типов личности
SELECT personality_type, COUNT(*) as count
FROM (
    SELECT
        CASE
            WHEN COUNT(*) FILTER (WHERE t.energy >= 0.6 AND t.valence >= 0.6) > COUNT(*) * 0.30
                THEN 'Эйфорический экстраверт'
            WHEN COUNT(*) FILTER (WHERE t.energy >= 0.6 AND t.valence < 0.45) > COUNT(*) * 0.30
                THEN 'Тревожный активист'
            WHEN COUNT(*) FILTER (WHERE t.energy < 0.5  AND t.valence < 0.45) > COUNT(*) * 0.30
                THEN 'Меланхолик'
            WHEN COUNT(*) FILTER (WHERE t.energy < 0.5  AND t.valence >= 0.6) > COUNT(*) * 0.30
                THEN 'Созерцательный оптимист'
            WHEN COUNT(*) FILTER (WHERE t.energy >= 0.6 AND t.valence < 0.45) > COUNT(*) * 0.20
             AND COUNT(*) FILTER (WHERE t.energy < 0.5  AND t.valence < 0.45) > COUNT(*) * 0.20
                THEN 'Меланхолик с агрессией'
            WHEN COUNT(*) FILTER (WHERE t.energy >= 0.6 AND t.valence >= 0.6) > COUNT(*) * 0.20
             AND COUNT(*) FILTER (WHERE t.energy < 0.5  AND t.valence >= 0.6) > COUNT(*) * 0.20
                THEN 'Позитивный микс'
            ELSE 'Эмоционально нестабильный'
        END AS personality_type
    FROM users u
    JOIN playlists pl       ON pl.user_id = u.id
    JOIN playlist_tracks pt ON pt.playlist_id = pl.id
    JOIN tracks t           ON t.id = pt.track_id
    GROUP BY u.id
) AS personality_stats
GROUP BY personality_type
ORDER BY count DESC;

-- ============================================
-- 6. ОБЪЯСНЕНИЕ ЛОГИКИ
-- ============================================

/*
ЗОНЫ ТРЕКОВ:
1. Hype (energy ≥ 0.6, valence ≥ 0.6) — энергичный позитив
2. Aggressive (energy ≥ 0.6, valence < 0.45) — энергия + негатив
3. Sad (energy < 0.5, valence < 0.45) — тихо + грустно
4. Calm (energy < 0.5, valence ≥ 0.6) — тихо + позитивно

ТИПЫ ЛИЧНОСТИ:
- Если зона > 30% треков → доминирующий тип
- Если две зоны > 20% → смешанный тип
- Иначе → эмоционально нестабильный

ХАРАКТЕРИСТИКИ:
- energy: 0 = спокойно, 1 = интенсивно
- valence: 0 = грустно/темно, 1 = радостно/позитивно
*/
