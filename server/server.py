# server.py
# Simple Flask API to accept metrics and serve host data.
# Beginner-friendly, with minimal features to get started.

import os
import sqlite3
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # allow the frontend to call the API during development

# Configuration
DB_PATH = os.environ.get("DATABASE_URL", "metrics.db")
API_KEY = os.environ.get("API_KEY", "supersecret")

# Helper: get DB connection (uses sqlite3)
def get_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

# Create table if not exists
def init_db():
    conn = get_db()
    conn.executescript("""
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
    CREATE INDEX IF NOT EXISTS idx_host_ts ON metrics(hostname, ts DESC);
    """)
    conn.commit()
    conn.close()

# Basic payload validation
REQUIRED = [
    "hostname","ts","cpu_percent","cpu_count","mem_total","mem_used","mem_percent",
    "disk_total","disk_used","disk_percent","load1","load5","load15",
    "net_bytes_sent","net_bytes_recv"
]

def validate_payload(data):
    if not isinstance(data, dict):
        return False, "payload must be JSON object"
    for f in REQUIRED:
        if f not in data:
            return False, f"missing field: {f}"
    return True, None

# POST /metrics : agents send metrics here
@app.route("/metrics", methods=["POST"])
def metrics_post():
    key = request.headers.get("X-API-KEY", "")
    if key != API_KEY:
        return jsonify({"error": "invalid api key"}), 401

    data = request.get_json()
    ok, err = validate_payload(data)
    if not ok:
        return jsonify({"error": err}), 400

    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            """INSERT INTO metrics (
                hostname, ts, cpu_percent, cpu_count, mem_total, mem_used, mem_percent,
                disk_total, disk_used, disk_percent, load1, load5, load15,
                net_bytes_sent, net_bytes_recv
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                data["hostname"], data["ts"], float(data["cpu_percent"]), int(data["cpu_count"]),
                int(data["mem_total"]), int(data["mem_used"]), float(data["mem_percent"]),
                int(data["disk_total"]), int(data["disk_used"]), float(data["disk_percent"]),
                float(data["load1"]), float(data["load5"]), float(data["load15"]),
                int(data["net_bytes_sent"]), int(data["net_bytes_recv"])
            )
        )
        conn.commit()
    except Exception as e:
        return jsonify({"error": "db error", "detail": str(e)}), 500
    finally:
        conn.close()

    return jsonify({"status": "ok"}), 200

# GET /hosts : list hostnames + last seen timestamp
@app.route("/hosts", methods=["GET"])
def get_hosts():
    conn = get_db()
    rows = conn.execute("SELECT hostname, MAX(ts) AS last_seen FROM metrics GROUP BY hostname ORDER BY last_seen DESC").fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows]), 200

# GET /host/<hostname>/latest : latest metrics for hostname
@app.route("/host/<hostname>/latest", methods=["GET"])
def host_latest(hostname):
    conn = get_db()
    row = conn.execute("SELECT * FROM metrics WHERE hostname = ? ORDER BY ts DESC LIMIT 1", (hostname,)).fetchone()
    conn.close()
    if not row:
        return jsonify({"error": "not found"}), 404
    return jsonify(dict(row)), 200

# GET /host/<hostname>/history?limit=N : last N rows (default 100)
@app.route("/host/<hostname>/history", methods=["GET"])
def host_history(hostname):
    limit = request.args.get("limit", default=100, type=int)
    if limit <= 0 or limit > 10000:
        return jsonify({"error": "limit must be 1..10000"}), 400
    conn = get_db()
    rows = conn.execute("SELECT * FROM metrics WHERE hostname = ? ORDER BY ts DESC LIMIT ?", (hostname, limit)).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows]), 200

# Root route helps when running server alone
@app.route("/", methods=["GET"])
def root():
    return jsonify({"message": "Monitoring server is running"}), 200

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)
