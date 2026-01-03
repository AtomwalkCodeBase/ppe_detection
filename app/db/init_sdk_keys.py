import sqlite3
import os

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))
    )
)

DB_PATH = os.path.join(BASE_DIR, "labguard.db")

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS sdk_keys (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sdk_id TEXT NOT NULL UNIQUE,
    api_key TEXT NOT NULL UNIQUE,
    active INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS sdk_labs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sdk_id TEXT NOT NULL,
    lab_id TEXT NOT NULL,
    UNIQUE (sdk_id, lab_id)
)
""")

conn.commit()
conn.close()

print("sdk_keys and sdk_labs tables ready")
