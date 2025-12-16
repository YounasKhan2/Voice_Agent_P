import sqlite3
from pathlib import Path

db_path = Path(__file__).parent / 'db.sqlite3'
print(f"Checking database: {db_path}")
print(f"Database exists: {db_path.exists()}")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = [row[0] for row in cursor.fetchall()]
print(f"\nTables in database ({len(tables)} total):")
for table in tables:
    print(f"  - {table}")
    
# Check if conversation_user table exists
if 'conversation_user' in tables:
    cursor.execute("PRAGMA table_info(conversation_user)")
    columns = cursor.fetchall()
    print(f"\nconversation_user columns:")
    for col in columns:
        print(f"  - {col[1]} ({col[2]})")

conn.close()
