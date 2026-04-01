import psycopg2
import re
import sys

# Исправление кодировки для Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Database configuration
DB_CONFIG = {
    'host': 'shinkansen.proxy.rlwy.net',
    'port': 48403,
    'database': 'music_personality_db',
    'user': 'postgres',
    'password': 'QHAFImJPyIemSaqvrqYGTjwPOMzwhDRZ'
}

# Список треков в формате "Исполнитель - Название"
tracks_raw = """
PHARAOH - Caramel
PHARAOH, White Punk - Unplugged 2: Love Kills
PHARAOH, ЛСП - Порнозвезда
PHARAOH - Black Siemens
SODA LUV, BUSHIDO ZHO - Mi Amore
ЧБ - Город 3х перекрёстков
Рустам Батербиев - А на рассвете
Зануда - Папиросы
IVOXYGEN - INTERNET LOVE
UncleFlexxx - Bellingham
wavescale - луна
Crazy Frog - Axel F
5opka, MellSher - XXL
Zaret_khan - Моника
SLIMUS - Аурус
SLIMUS - Мой друг
INSTASAMKA - MONEYKEN LOVE
FRIENDLY THUG 52 NGG - You Only Live Once
Miyagi - Сонная лощина
GEKYUM - Сообщение
104, Скриптонит, LUCAVEROS - Проблемы
Баста, GUF - Не всё потеряно пока
пороксердца - Выпадет шанс
OVERHILL, Криспи, Экси, PUSSYKILLER - Разбитое сердце
9 грамм - Не для всех
Апология - Закат
PHARAOH - Без ключа
BATO - Ночь Спит Днем
Miyagi & Эндшпиль, MAXIFAM - Без обид
xe1to, ENTYPE - God Bless
Каста - Ды-ды-дым
KRISTIEE - романтик
DSPRITE - Парфюм
PHARAOH - Может Расскажешь, Что Ты Чувствуешь (Главные Ворота)
УННВ - Дневной позор
FRIENDLY THUG 52 NGG - Earth Walker 100
Diamondset - FASHION
Diamondset - Лучший
LOURENZ - 2к17
Элджей - V ecstase
пороксердца - Это пройдет быстро
4К - Шифры
nexizes - сборник фото
Miyagi & Эндшпиль, масло черного тмина - Wisdom
Miyagi & Эндшпиль, Крип-А-Крип - Action
Miyagi & Эндшпиль, Скриптонит - Quartz
Miyagi & Эндшпиль, TumaniYO - Boom Bap
Miyagi & Эндшпиль - Scary move
Miyagi & Эндшпиль, TumaniYO - Sample
"""

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
    elif 'уннв' in artist_lower:
        genre = 'rap'
    elif 'каста' in artist_lower:
        genre = 'rap'
    elif any(x in artist_lower for x in ['батербиев', 'зарет', 'джанмирзоев']):
        genre = 'caucasian pop'
    elif 'crazy frog' in artist_lower:
        genre = 'dance'
    elif any(x in artist_lower for x in ['nexizes', 'пороксердца', 'wavescale']):
        genre = 'indie'
    elif 'kristiee' in artist_lower:
        genre = 'pop'
    
    # Определение energy (0.0-1.0)
    energy = 0.65  # по умолчанию
    
    if any(x in title_lower for x in ['phonk', 'trap', 'drill']):
        energy = 0.80
    elif any(x in title_lower for x in ['грустн', 'sad', 'тоск', 'слез', 'плач']):
        energy = 0.50
    elif any(x in title_lower for x in ['dance', 'party', 'club']):
        energy = 0.75
    elif 'уннв' in artist_lower:
        energy = 0.60
    
    # Определение valence (0.0-1.0) - позитивность
    valence = 0.50  # по умолчанию
    
    if any(x in title_lower for x in ['love', 'люб', 'счаст', 'happy']):
        valence = 0.60
    elif any(x in title_lower for x in ['грустн', 'sad', 'слез', 'плач', 'боль', 'разбит']):
        valence = 0.30
    elif any(x in title_lower for x in ['party', 'dance', 'club']):
        valence = 0.70
    elif 'pharaoh' in artist_lower:
        valence = 0.40
    elif 'уннв' in artist_lower:
        valence = 0.35
    
    return genre, energy, valence


def parse_tracks(raw_text):
    """
    Парсит текст с треками в формате "Исполнитель - Название"
    """
    tracks = []
    lines = raw_text.strip().split('\n')
    
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
                print(f"[-] Пропущен (дубликат): {track['artist']} - {track['title']}")
                
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
    
    # Парсим треки
    tracks = parse_tracks(tracks_raw)
    print(f"Найдено треков для вставки: {len(tracks)}")
    print()
    
    # Вставляем в БД
    inserted, skipped = insert_tracks(tracks)
    
    print()
    print("=" * 60)
    print(f"РЕЗУЛЬТАТ:")
    print(f"  Добавлено: {inserted}")
    print(f"  Пропущено: {skipped}")
    print(f"  Всего: {len(tracks)}")
    print("=" * 60)
