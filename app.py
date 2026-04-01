from flask import Flask, request, jsonify, render_template
import psycopg2
import requests
import json

app = Flask(__name__)

# Database configuration
DB_CONFIG = {
    'host': 'shinkansen.proxy.rlwy.net',
    'port': 48403,
    'database': 'music_personality_db',
    'user': 'postgres',
    'password': 'QHAFImJPyIemSaqvrqYGTjwPOMzwhDRZ'
}

# OpenRouter API configuration
OPENROUTER_API_KEY = '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'
OPENROUTER_URL = 'https://openrouter.ai/api/v1/chat/completions'
OPENROUTER_SITE_URL = 'https://music-personality-db.com'
OPENROUTER_APP_NAME = 'Music Personality Analyzer'

def get_db_connection():
    """Create database connection"""
    return psycopg2.connect(**DB_CONFIG)

def get_track_characteristics(tracks):
    """Get energy and valence for tracks using OpenRouter API"""
    
    # First, let's check what models are available
    try:
        models_response = requests.get('https://openrouter.ai/api/v1/models', 
                                      headers={'Authorization': f'Bearer {OPENROUTER_API_KEY}'})
        print(f"Models API status: {models_response.status_code}")
        if models_response.status_code == 200:
            available_models = models_response.json()
            print(f"Available models count: {len(available_models.get('data', []))}")
            free_models = [m['id'] for m in available_models.get('data', []) if 'free' in m['id'].lower()]
            print(f"Free models: {free_models[:5]}")  # Show first 5
    except Exception as e:
        print(f"Could not fetch models list: {e}")
    
    prompt = f"""You are a music analysis expert. Analyze these tracks and return ONLY a JSON array with precise energy, valence, and genre.

Tracks to analyze:
{json.dumps(tracks, ensure_ascii=False)}

IMPORTANT GUIDELINES:
- Energy (0.0-1.0): Physical intensity, loudness, tempo, dynamics
  * 0.0-0.3: Very calm, slow, quiet (ballads, ambient)
  * 0.3-0.5: Moderate, relaxed (soft pop, acoustic)
  * 0.5-0.7: Energetic, upbeat (pop, dance)
  * 0.7-0.9: Very energetic, intense (rock, EDM)
  * 0.9-1.0: Extremely intense (metal, hardcore)

- Valence (0.0-1.0): Emotional positivity
  * 0.0-0.3: Very sad, dark, depressive
  * 0.3-0.5: Melancholic, bittersweet
  * 0.5-0.7: Neutral to positive
  * 0.7-0.9: Happy, uplifting, joyful
  * 0.9-1.0: Euphoric, extremely positive

- Genre: Be specific and descriptive
  * Examples: "Romantic rap", "Sad rap", "Dance pop", "Soft pop", "Dark rap", "Lyrical rap"
  * Use 1-2 words that capture the style and mood

Return ONLY this JSON format (no other text):
[
  {{"title": "track name", "artist": "artist name", "genre": "Romantic rap", "energy": 0.75, "valence": 0.60}},
  ...
]

Be precise and consider the actual sound and mood of each track."""

    headers = {
        'Authorization': f'Bearer {OPENROUTER_API_KEY}',
        'Content-Type': 'application/json',
        'HTTP-Referer': OPENROUTER_SITE_URL,
        'X-Title': OPENROUTER_APP_NAME
    }
    
    # Try primary model first, then fallback
    models = [
        'nvidia/llama-3.1-nemotron-70b-instruct',  # NVIDIA first
        'nvidia/nemotron-3-super-120b-a12b:free',
        'openrouter/free',  # Generic free model
        'minimax/minimax-m2.5:free',
        'stepfun/step-3.5-flash:free',
        'arcee-ai/trinity-large-preview:free'
    ]
    
    for model in models:
        data = {
            'model': model,
            'messages': [
                {'role': 'user', 'content': prompt}
            ]
        }
        
        try:
            print(f"Trying model: {model}")
            response = requests.post(OPENROUTER_URL, headers=headers, json=data, timeout=60)
            print(f"OpenRouter response status: {response.status_code}")
            
            if response.status_code == 404:
                print(f"Model {model} not found, trying next...")
                continue
                
            response.raise_for_status()
            
            result = response.json()
            print(f"OpenRouter response keys: {result.keys()}")
            
            if 'choices' not in result or len(result['choices']) == 0:
                print(f"No choices in response, trying next model...")
                continue
                
            content = result['choices'][0]['message']['content']
            print(f"Content preview: {content[:200]}...")
            
            # Extract JSON from response
            start = content.find('[')
            end = content.rfind(']') + 1
            
            if start == -1 or end == 0:
                print("No JSON array found in response")
                continue
                
            json_str = content[start:end]
            parsed = json.loads(json_str)
            print(f"Successfully parsed {len(parsed)} tracks")
            return parsed
            
        except requests.exceptions.RequestException as e:
            print(f"Request error with {model}: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response text: {e.response.text}")
            continue
        except Exception as e:
            print(f"Error with {model}: {e}")
            import traceback
            traceback.print_exc()
            continue
    
    print("All models failed")
    return None

def analyze_personality(user_id, conn=None):
    """Run personality analysis query"""
    print(f"Starting analyze_personality for user_id={user_id}")
    
    # Use provided connection or create new one
    close_conn = False
    if conn is None:
        close_conn = True
        try:
            conn = get_db_connection()
        except Exception as e:
            print(f"Database connection error: {e}")
            return None
    
    cur = conn.cursor()
    
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
            -- Сначала явные доминанты (>35%)
            WHEN COUNT(*) FILTER (WHERE t.energy >= 0.65 AND t.valence >= 0.6) > COUNT(*) * 0.35
                THEN 'Эйфорический'
            WHEN COUNT(*) FILTER (WHERE t.energy >= 0.65 AND t.valence < 0.4) > COUNT(*) * 0.35
                THEN 'Тревожно-агрессивный'
            WHEN COUNT(*) FILTER (WHERE t.energy < 0.65 AND t.valence < 0.4) > COUNT(*) * 0.35
                THEN 'Меланхолический'
            WHEN COUNT(*) FILTER (WHERE t.energy < 0.65 AND t.valence >= 0.55) > COUNT(*) * 0.35
                THEN 'Спокойно-оптимистичный'
            
            -- Смешанные типы
            WHEN COUNT(*) FILTER (WHERE t.energy >= 0.65 AND t.valence < 0.4) >= COUNT(*) * 0.18
             AND COUNT(*) FILTER (WHERE t.energy < 0.65 AND t.valence < 0.4) >= COUNT(*) * 0.18
                THEN 'Депрессивно-агрессивный'
            WHEN COUNT(*) FILTER (WHERE t.energy >= 0.65 AND t.valence >= 0.6) >= COUNT(*) * 0.18
             AND COUNT(*) FILTER (WHERE t.energy < 0.65 AND t.valence >= 0.55) >= COUNT(*) * 0.18
                THEN 'Позитивно-уравновешенный'
            
            -- Определяем по МАКСИМАЛЬНОЙ зоне (если нет явного доминанта)
            WHEN GREATEST(
                COUNT(*) FILTER (WHERE t.energy >= 0.65 AND t.valence >= 0.6),
                COUNT(*) FILTER (WHERE t.energy >= 0.65 AND t.valence < 0.4),
                COUNT(*) FILTER (WHERE t.energy < 0.65 AND t.valence < 0.4),
                COUNT(*) FILTER (WHERE t.energy < 0.65 AND t.valence >= 0.55)
            ) = COUNT(*) FILTER (WHERE t.energy >= 0.65 AND t.valence >= 0.6)
                THEN 'Эйфорический'
            WHEN GREATEST(
                COUNT(*) FILTER (WHERE t.energy >= 0.65 AND t.valence >= 0.6),
                COUNT(*) FILTER (WHERE t.energy >= 0.65 AND t.valence < 0.4),
                COUNT(*) FILTER (WHERE t.energy < 0.65 AND t.valence < 0.4),
                COUNT(*) FILTER (WHERE t.energy < 0.65 AND t.valence >= 0.55)
            ) = COUNT(*) FILTER (WHERE t.energy >= 0.65 AND t.valence < 0.4)
                THEN 'Тревожно-агрессивный'
            WHEN GREATEST(
                COUNT(*) FILTER (WHERE t.energy >= 0.65 AND t.valence >= 0.6),
                COUNT(*) FILTER (WHERE t.energy >= 0.65 AND t.valence < 0.4),
                COUNT(*) FILTER (WHERE t.energy < 0.65 AND t.valence < 0.4),
                COUNT(*) FILTER (WHERE t.energy < 0.65 AND t.valence >= 0.55)
            ) = COUNT(*) FILTER (WHERE t.energy < 0.65 AND t.valence < 0.4)
                THEN 'Меланхолический'
            WHEN GREATEST(
                COUNT(*) FILTER (WHERE t.energy >= 0.65 AND t.valence >= 0.6),
                COUNT(*) FILTER (WHERE t.energy >= 0.65 AND t.valence < 0.4),
                COUNT(*) FILTER (WHERE t.energy < 0.65 AND t.valence < 0.4),
                COUNT(*) FILTER (WHERE t.energy < 0.65 AND t.valence >= 0.55)
            ) = COUNT(*) FILTER (WHERE t.energy < 0.65 AND t.valence >= 0.55)
                THEN 'Спокойно-оптимистичный'
            
            ELSE 'Сбалансированный'
        END AS personality_type
    FROM users u
    JOIN playlists pl ON pl.user_id = u.id
    JOIN playlist_tracks pt ON pt.playlist_id = pl.id
    JOIN tracks t ON t.id = pt.track_id
    WHERE u.id = %s
    GROUP BY u.name, u.age, u.gender;
    """
    
    try:
        # Use string substitution instead of parameterized query due to psycopg2 issue
        # Safe because user_id is an integer
        query_with_id = query.replace('%s', str(user_id))
        cur.execute(query_with_id)
        result = cur.fetchone()
        
        print(f"Query result: {result}")  # Debug
        
        if result is None:
            print(f"No data found for user_id={user_id}")
            cur.close()
            if close_conn:
                conn.close()
            return None
        
        cur.close()
        if close_conn:
            conn.close()
        
        return {
            'name': result[0],
            'age': result[1],
            'gender': result[2],
            'hype_ratio': float(result[3]) if result[3] is not None else 0.0,
            'aggressive_ratio': float(result[4]) if result[4] is not None else 0.0,
            'sad_ratio': float(result[5]) if result[5] is not None else 0.0,
            'calm_ratio': float(result[6]) if result[6] is not None else 0.0,
            'personality_type': result[7] if result[7] is not None else 'Неопределенный'
        }
    except Exception as e:
        print(f"Error executing query: {e}")
        import traceback
        traceback.print_exc()
        if close_conn:
            conn.close()
        return None

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/green')
def index_green():
    """Green theme page"""
    return render_template('index_green.html')

@app.route('/dark')
def index_dark_green():
    """Dark green theme page"""
    return render_template('index_dark_green.html')

@app.route('/red')
def index_red():
    """Red theme page"""
    return render_template('index_red.html')

@app.route('/lofi')
def index_lofi():
    """Lo-fi theme page"""
    return render_template('index_lofi.html')

@app.route('/trap')
def index_trap():
    """Trap theme page"""
    return render_template('index_trap.html')

@app.route('/indie')
def index_indie():
    """Indie theme page"""
    return render_template('index_indie.html')

@app.route('/synthwave')
def index_synthwave():
    """Synthwave theme page"""
    return render_template('index_synthwave.html')

@app.route('/classical')
def index_classical():
    """Classical theme page"""
    return render_template('index_classical.html')

@app.route('/ambient')
def index_ambient():
    """Ambient theme page"""
    return render_template('index_ambient.html')

@app.route('/cinematic')
def index_cinematic():
    """Cinematic theme page"""
    return render_template('index_cinematic.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    """Analyze user's playlist"""
    data = request.json
    
    name = data.get('name')
    age = data.get('age')
    gender = data.get('gender')
    tracks = data.get('tracks', [])
    
    print(f"Raw request.json: {request.json}")
    print(f"Received tracks from frontend: {tracks}")
    if tracks:
        print(f"First track: title='{tracks[0].get('title')}', artist='{tracks[0].get('artist')}'")
    
    if not name or not tracks or len(tracks) < 1:
        return jsonify({'error': 'Нужно указать имя и хотя бы 1 трек'}), 400
    
    # Save to database
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Insert user
        cur.execute(
            "INSERT INTO users (name, age, gender) VALUES (%s, %s, %s) RETURNING id",
            (name, age, gender)
        )
        user_id = cur.fetchone()[0]
        
        # Insert playlist
        cur.execute(
            "INSERT INTO playlists (user_id, title, mood) VALUES (%s, %s, %s) RETURNING id",
            (user_id, f'Плейлист {name}', 'смешанный')
        )
        playlist_id = cur.fetchone()[0]
        
        # Check tracks in template table first, then in regular tracks table
        tracks_to_analyze = []
        known_characteristics = {}
        
        for track in tracks:
            title = track['title']
            artist = track.get('artist', 'Unknown')
            
            # First, check in track_templates (priority)
            cur.execute(
                "SELECT genre, energy, valence FROM track_templates WHERE LOWER(title) = LOWER(%s) AND LOWER(artist) = LOWER(%s) LIMIT 1",
                (title, artist)
            )
            template = cur.fetchone()
            
            if template:
                # Found in templates, use these characteristics
                known_characteristics[f"{title}|{artist}"] = {
                    'title': title,
                    'artist': artist,
                    'genre': template[0],
                    'energy': float(template[1]),
                    'valence': float(template[2]),
                    'source': 'template'
                }
                print(f"Found in templates: {title} - {artist}")
            else:
                # Not in templates, check in regular tracks table
                cur.execute(
                    "SELECT genre, energy, valence FROM tracks WHERE LOWER(title) = LOWER(%s) AND LOWER(artist) = LOWER(%s) LIMIT 1",
                    (title, artist)
                )
                existing = cur.fetchone()
                
                if existing:
                    # Found in tracks, copy characteristics
                    known_characteristics[f"{title}|{artist}"] = {
                        'title': title,
                        'artist': artist,
                        'genre': existing[0],
                        'energy': float(existing[1]),
                        'valence': float(existing[2]),
                        'source': 'existing'
                    }
                    print(f"Found in tracks: {title} - {artist}")
                else:
                    # Not found anywhere, need to analyze with AI
                    tracks_to_analyze.append(track)
                    print(f"Need to analyze: {title} - {artist}")
        
        # Get characteristics only for unknown tracks
        if tracks_to_analyze:
            print(f"Analyzing {len(tracks_to_analyze)} tracks with AI...")
            characteristics = get_track_characteristics(tracks_to_analyze)
            
            if not characteristics:
                return jsonify({'error': 'Не удалось получить характеристики треков'}), 500
        else:
            print("All tracks found in database, no AI analysis needed!")
            characteristics = []
        
        # Build characteristics map from API results
        api_characteristics = {}
        for track_data in characteristics:
            key = f"{track_data['title']}|{track_data.get('artist', 'Unknown')}"
            api_characteristics[key] = track_data
            print(f"API characteristic key: '{key}'")
            
            # Add new AI-analyzed tracks to track_templates for future use
            title = track_data['title']
            artist = track_data.get('artist', 'Unknown')
            genre = track_data.get('genre', 'Unknown')
            energy = track_data['energy']
            valence = track_data['valence']
            
            try:
                cur.execute(
                    """INSERT INTO track_templates (title, artist, genre, energy, valence) 
                       VALUES (%s, %s, %s, %s, %s) 
                       ON CONFLICT (title, artist) DO NOTHING""",
                    (title, artist, genre, energy, valence)
                )
                print(f"Added to templates: {title} - {artist}")
            except Exception as e:
                print(f"Warning: Could not add to templates: {title} - {artist}, Error: {e}")
        
        # Insert all tracks and link to playlist
        for i, track in enumerate(tracks):
            title = track['title']
            artist = track.get('artist', 'Unknown')
            key = f"{title}|{artist}"
            
            print(f"Processing track {i+1}: title='{title}', artist='{artist}', key='{key}'")
            
            # Get characteristics from known or API
            if key in known_characteristics:
                # Use known characteristics (from templates or existing tracks)
                track_data = known_characteristics[key]
            elif key in api_characteristics:
                # Use AI-analyzed characteristics
                track_data = api_characteristics[key]
            else:
                # Fallback (shouldn't happen)
                print(f"Warning: No characteristics found for {title} - {artist}")
                continue
            
            # Insert track (always create new record)
            cur.execute(
                """INSERT INTO tracks (title, artist, genre, energy, valence) 
                   VALUES (%s, %s, %s, %s, %s) RETURNING id""",
                (title, artist, track_data.get('genre', 'Unknown'), 
                 track_data['energy'], track_data['valence'])
            )
            track_id = cur.fetchone()[0]
            
            # Link to playlist
            cur.execute(
                "INSERT INTO playlist_tracks (playlist_id, track_id, position) VALUES (%s, %s, %s)",
                (playlist_id, track_id, i + 1)
            )
        
        conn.commit()
        
        # Analyze personality (use same connection)
        result = analyze_personality(user_id, conn)
        
        cur.close()
        conn.close()
        
        if result is None:
            return jsonify({'error': 'Не удалось проанализировать личность. Проверьте логи.'}), 500
        
        return jsonify(result)
        
    except Exception as e:
        conn.rollback()
        cur.close()
        conn.close()
        return jsonify({'error': f'Ошибка базы данных: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
