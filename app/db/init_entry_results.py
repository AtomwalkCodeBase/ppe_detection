import sqlite3, os

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))
    )
)
DB_PATH = os.path.join(BASE_DIR, "labguard.db")

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS entry_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lab_id TEXT,
    user_id TEXT,
    sdk_id TEXT,
    compliant INTEGER,
    detected_ppe TEXT,
    missing_ppe TEXT,
    snapshot_path TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

conn.commit()
conn.close()

print("entry_results table created")
