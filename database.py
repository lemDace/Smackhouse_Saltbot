# database.py
import sqlite3
import json
from config import DEFAULT_CONFIG

DB_PATH = "saltbot.sqlite3"
conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

def setup_tables():
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            salt REAL NOT NULL DEFAULT 0
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS history (
            user_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            amount REAL NOT NULL,
            PRIMARY KEY (user_id, date)
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS config (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
    """)
    conn.commit()

def seed_config():
    cur.execute("SELECT COUNT(*) AS c FROM config")
    if cur.fetchone()["c"] == 0:
        for k, v in DEFAULT_CONFIG.items():
            cur.execute("INSERT OR REPLACE INTO config (key, value) VALUES (?, ?)", (k, json.dumps(v)))
        conn.commit()

def get_config():
    cur.execute("SELECT key, value FROM config")
    rows = cur.fetchall()
    cfg = {row["key"]: json.loads(row["value"]) for row in rows}
    cfg["curse_words"] = set(cfg.get("curse_words", []))
    cfg["insult_words"] = set(cfg.get("insult_words", []))
    cfg["ranks"] = [[float(t), str(n)] for t, n in cfg.get("ranks", [])]
    if "mention_amplifies" not in cfg:
        cfg["mention_amplifies"] = True
    return cfg

def save_config_key(key, value):
    cur.execute("INSERT OR REPLACE INTO config (key, value) VALUES (?, ?)", (key, json.dumps(value)))
    conn.commit()
