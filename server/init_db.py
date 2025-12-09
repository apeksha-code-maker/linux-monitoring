# init_db.py - initialize the SQLite DB for the server
import os
import sqlite3

DB_PATH = os.environ.get("DATABASE_URL", "metrics.db")

schema = """
CREATE TABLE IF NOT EXISTS metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    hostname TEXT NOT NULL,
    ts TEXT NOT NULL,
    cpu_percent REAL,
    cpu_count INTEGER,
    mem_total INTEGER,
    mem_used INTEGER,
    mem_percent REAL,
    disk_total INTEGER,
    disk_used INTEGER,
    disk_percent REAL,
    load1 REAL,
    load5 REAL,
    load15 REAL,
    net_bytes_sent INTEGER,
    net_bytes_recv INTEGER
);
CREATE INDEX IF NOT EXISTS idx_hostname_ts ON metrics(hostname, ts DESC);
"""

def init_db(path=DB_PATH):
    conn = sqlite3.connect(path)
    conn.executescript(schema)
    conn.commit()
    conn.close()
    print("Initialized DB at", path)

if __name__ == "__main__":
    init_db()

