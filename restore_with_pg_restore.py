import subprocess
import sys

# Try to restore using pg_restore
backup_file = 'Бекап на 24.03.sql'

# Connection string
conn_string = "postgresql://postgres:QHAFImJPyIemSaqvrqYGTjwPOMzwhDRZ@shinkansen.proxy.rlwy.net:48403/music_personality_db"

print("Attempting to restore using pg_restore...")

try:
    # Try pg_restore
    result = subprocess.run(
        ['pg_restore', '-d', conn_string, '-c', '-v', backup_file],
        capture_output=True,
        text=True
    )
    
    print("STDOUT:", result.stdout)
    print("STDERR:", result.stderr)
    print("Return code:", result.returncode)
    
except FileNotFoundError:
    print("pg_restore not found. Trying alternative method...")
    
    # Alternative: use psql with custom format
    try:
        result = subprocess.run(
            ['psql', conn_string, '-f', backup_file],
            capture_output=True,
            text=True
        )
        print("STDOUT:", result.stdout)
        print("STDERR:", result.stderr)
    except FileNotFoundError:
        print("psql not found either.")
        print("\nPlease install PostgreSQL client tools or restore manually through pgAdmin.")
        print(f"Backup file: {backup_file}")
        sys.exit(1)
