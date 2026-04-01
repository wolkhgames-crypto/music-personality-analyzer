-- Создание таблицы-справочника для эталонных треков
CREATE TABLE IF NOT EXISTS track_templates (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    artist VARCHAR(255) NOT NULL,
    genre VARCHAR(100),
    energy DECIMAL(3,2) CHECK (energy >= 0 AND energy <= 1),
    valence DECIMAL(3,2) CHECK (valence >= 0 AND valence <= 1),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(title, artist)  -- Предотвращает дубликаты
);

-- Создание индекса для быстрого поиска
CREATE INDEX idx_track_templates_title_artist ON track_templates(LOWER(title), LOWER(artist));

-- Примеры популярных треков (можешь добавить свои)
INSERT INTO track_templates (title, artist, genre, energy, valence) VALUES
('Blinding Lights', 'The Weeknd', 'Synth-pop', 0.73, 0.33),
('Shape of You', 'Ed Sheeran', 'Pop', 0.65, 0.93),
('Someone Like You', 'Adele', 'Ballad', 0.40, 0.23),
('Smells Like Teen Spirit', 'Nirvana', 'Grunge', 0.93, 0.43),
('Bohemian Rhapsody', 'Queen', 'Rock', 0.55, 0.50)
ON CONFLICT (title, artist) DO NOTHING;

-- Комментарий к таблице
COMMENT ON TABLE track_templates IS 'Справочник эталонных треков с предустановленными характеристиками для быстрого анализа';
