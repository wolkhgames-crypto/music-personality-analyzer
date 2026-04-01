-- Проверка всех таблиц и их связей

-- 1. Пользователи
SELECT 'USERS' as table_name, COUNT(*) as count FROM users;
SELECT * FROM users ORDER BY id;

-- 2. Плейлисты
SELECT 'PLAYLISTS' as table_name, COUNT(*) as count FROM playlists;
SELECT * FROM playlists ORDER BY id;

-- 3. Треки
SELECT 'TRACKS' as table_name, COUNT(*) as count FROM tracks;
SELECT id, title, artist, genre, energy, valence FROM tracks ORDER BY id LIMIT 10;

-- 4. Связи плейлист-треки
SELECT 'PLAYLIST_TRACKS' as table_name, COUNT(*) as count FROM playlist_tracks;
SELECT * FROM playlist_tracks ORDER BY playlist_id, position LIMIT 20;

-- 5. Шаблоны треков
SELECT 'TRACK_TEMPLATES' as table_name, COUNT(*) as count FROM track_templates;
SELECT id, title, artist, genre, energy, valence FROM track_templates ORDER BY id LIMIT 10;

-- 6. Проверка связей (user -> playlist -> tracks)
SELECT 
    u.id as user_id,
    u.name as user_name,
    p.id as playlist_id,
    p.title as playlist_title,
    p.mood,
    COUNT(pt.track_id) as tracks_count
FROM users u
JOIN playlists p ON p.user_id = u.id
LEFT JOIN playlist_tracks pt ON pt.playlist_id = p.id
GROUP BY u.id, u.name, p.id, p.title, p.mood
ORDER BY u.id;

-- 7. Проверка что ID совпадают
SELECT 
    u.id as user_id,
    p.id as playlist_id,
    CASE WHEN u.id = p.id THEN 'OK' ELSE 'MISMATCH' END as status
FROM users u
JOIN playlists p ON p.user_id = u.id
ORDER BY u.id;
