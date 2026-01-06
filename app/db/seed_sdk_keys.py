import sqlite3
import os

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))
    )
)

DB_PATH = os.path.join(BASE_DIR, "labguard.db")

SDK_ID = "SDK-NET-01"
API_KEY = "SDK_NET_01_SECRET"

LABS = ["LAB-01", "LAB-02"]

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

cur.execute("""
INSERT OR IGNORE INTO sdk_keys (sdk_id, api_key, active)
VALUES (?, ?, 1)
""", (SDK_ID, API_KEY))

for lab in LABS:
    cur.execute("""
    INSERT OR IGNORE INTO sdk_labs (sdk_id, lab_id)
    VALUES (?, ?)
    """, (SDK_ID, lab))

conn.commit()
conn.close()

print("✅ SDK seeded with labs")
