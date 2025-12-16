import sqlite3
from pathlib import Path

db_path = Path(__file__).parent / 'db.sqlite3'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("SELECT app, name, applied FROM django_migrations WHERE app='conversation' ORDER BY applied")
migrations = cursor.fetchall()

print("Applied migrations for 'conversation' app:")
for app, name, applied in migrations:
    print(f"  [{app}] {name} - {applied}")

conn.close()
