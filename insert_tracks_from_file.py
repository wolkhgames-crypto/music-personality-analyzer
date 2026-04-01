import psycopg2
import sys

# Исправление кодировки для Windows
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

# Database configuration
DB_CONFIG = {
    'host': 'shinkansen.proxy.rlwy.net',
    'port': 48403,
    'database': 'music_personality_db',
    'user': 'postgres',
    'password': 'QHAFImJPyIemSaqvrqYGTjwPOMzwhDRZ'
}

def analyze_track(artist, title):
    """
    Анализирует трек и возвращает жанр, energy, valence
    """
    artist_lower = artist.lower()
    title_lower = title.lower()
    
    # Определение жанра
    genre = 'rap'  # по умолчанию
    
    if 'miyagi' in artist_lower or 'эндшпиль' in artist_lower:
        genre = 'rap'
    elif 'pharaoh' in artist_lower:
        genre = 'rap'
    elif 'баста' in artist_lower or 'guf' in artist_lower:
        genre = 'rap'
    elif 'уннв' in artist_lower or 'yннв' in artist_lower:
        genre = 'rap'
    elif 'каста' in artist_lower:
        genre = 'rap'
    elif 'скриптонит' in artist_lower:
        genre = 'rap'
    elif 'big baby tape' in artist_lower or 'kizaru' in artist_lower:
        genre = 'rap'
    elif any(x in artist_lower for x in ['батербиев', 'зарет', 'джанмирзоев', 'тхагалегов']):
        genre = 'caucasian pop'
    elif 'crazy frog' in artist_lower:
        genre = 'dance'
    elif any(x in artist_lower for x in ['nexizes', 'пороксердца', 'wavescale']):
        genre = 'indie'
    elif 'kristiee' in artist_lower:
        genre = 'pop'
    elif 'eminem' in artist_lower or 'drake' in artist_lower or '2pac' in artist_lower:
        genre = 'hip-hop'
    elif 'король и шут' in artist_lower or 'сектор газа' in artist_lower:
        genre = 'punk rock'
    
    # Определение energy (0.0-1.0)
    energy = 0.60  # по умолчанию снижено
    
    if any(x in title_lower for x in ['phonk', 'trap', 'drill']):
        energy = 0.75
    elif any(x in title_lower for x in ['грустн', 'sad', 'тоск', 'слез', 'плач', 'одиноч']):
        energy = 0.45
    elif any(x in title_lower for x in ['dance', 'party', 'club']):
        energy = 0.70
    elif 'уннв' in artist_lower or 'yннв' in artist_lower:
        energy = 0.55
    elif 'pharaoh' in artist_lower:
        energy = 0.60
    
    # Определение valence (0.0-1.0) - позитивность
    valence = 0.45  # по умолчанию снижено
    
    if any(x in title_lower for x in ['love', 'люб', 'счаст', 'happy']):
        valence = 0.55
    elif any(x in title_lower for x in ['грустн', 'sad', 'слез', 'плач', 'боль', 'разбит', 'одиноч']):
        valence = 0.25
    elif any(x in title_lower for x in ['party', 'dance', 'club']):
        valence = 0.65
    elif 'pharaoh' in artist_lower:
        valence = 0.35
    elif 'уннв' in artist_lower or 'yннв' in artist_lower:
        valence = 0.30
    
    return genre, energy, valence


def parse_tracks_from_file(filename):
    """
    Читает треки из файла в формате "Исполнитель - Название"
    """
    tracks = []
    
    # Пробуем разные кодировки
    encodings = ['utf-8', 'utf-8-sig', 'cp1251', 'windows-1251', 'latin-1']
    lines = []
    
    for encoding in encodings:
        try:
            with open(filename, 'r', encoding=encoding) as f:
                lines = f.readlines()
            print(f"[i] Файл прочитан с кодировкой: {encoding}")
            break
        except (UnicodeDecodeError, FileNotFoundError) as e:
            if isinstance(e, FileNotFoundError):
                print(f"[!] Файл {filename} не найден!")
                return tracks
            continue
    
    if not lines:
        print(f"[!] Не удалось прочитать файл {filename} ни с одной кодировкой")
        return tracks
    
    for line in lines:
        line = line.strip()
        if not line or ' - ' not in line:
            continue
        
        # Разделяем по первому " - "
        parts = line.split(' - ', 1)
        if len(parts) != 2:
            continue
        
        artist = parts[0].strip()
        title = parts[1].strip()
        
        # Берем первого исполнителя если их несколько
        if ',' in artist:
            artist = artist.split(',')[0].strip()
        
        genre, energy, valence = analyze_track(artist, title)
        
        tracks.append({
            'title': title,
            'artist': artist,
            'genre': genre,
            'energy': energy,
            'valence': valence
        })
    
    return tracks


def insert_tracks(tracks):
    """
    Вставляет треки в базу данных
    """
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    inserted = 0
    skipped = 0
    
    for track in tracks:
        try:
            cur.execute(
                """INSERT INTO track_templates (title, artist, genre, energy, valence) 
                   VALUES (%s, %s, %s, %s, %s) 
                   ON CONFLICT (title, artist) DO NOTHING""",
                (track['title'], track['artist'], track['genre'], 
                 track['energy'], track['valence'])
            )
            
            if cur.rowcount > 0:
                inserted += 1
                print(f"[+] Добавлен: {track['artist']} - {track['title']}")
            else:
                skipped += 1
                # print(f"[-] Пропущен (дубликат): {track['artist']} - {track['title']}")
                
        except Exception as e:
            print(f"[!] Ошибка при добавлении {track['artist']} - {track['title']}: {e}")
            skipped += 1
    
    conn.commit()
    cur.close()
    conn.close()
    
    return inserted, skipped


if __name__ == '__main__':
    print("=" * 60)
    print("АВТОМАТИЧЕСКАЯ ВСТАВКА ТРЕКОВ В track_templates")
    print("=" * 60)
    print()
    
    # Читаем треки из файла
    filename = 'all_tracks.txt'
    tracks = parse_tracks_from_file(filename)
    
    if not tracks:
        print(f"[!] Не найдено треков в файле {filename}")
        print(f"[!] Создайте файл {filename} и добавьте треки в формате:")
        print(f"    Исполнитель - Название")
        sys.exit(1)
    
    print(f"Найдено треков для вставки: {len(tracks)}")
    print()
    
    # Вставляем в БД
    inserted, skipped = insert_tracks(tracks)
    
    print()
    print("=" * 60)
    print(f"РЕЗУЛЬТАТ:")
    print(f"  Добавлено: {inserted}")
    print(f"  Пропущено (дубликаты): {skipped}")
    print(f"  Всего: {len(tracks)}")
    print("=" * 60)
