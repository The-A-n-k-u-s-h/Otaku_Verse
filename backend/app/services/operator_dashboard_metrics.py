"""Anonymous live visitor tracking and dashboard counters."""
import os, sqlite3, time, secrets
from flask import current_app, request, session

def _path():
    return current_app.config.get("WAIFU_DATABASE") or os.path.join(current_app.instance_path, "waifu_matching.sqlite3")

def init_operator_metrics(app):
    path = app.config.get("WAIFU_DATABASE") or os.path.join(app.instance_path, "waifu_matching.sqlite3")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with sqlite3.connect(path) as db:
        db.execute("""CREATE TABLE IF NOT EXISTS visitor_presence (
            visitor_key TEXT PRIMARY KEY, first_seen INTEGER NOT NULL,
            last_seen INTEGER NOT NULL, path TEXT NOT NULL DEFAULT '/')""")
        db.execute("CREATE INDEX IF NOT EXISTS idx_visitor_presence_last_seen ON visitor_presence(last_seen)")

def heartbeat():
    key = session.get("visitor_presence_key")
    if not key:
        key = secrets.token_urlsafe(24)
        session["visitor_presence_key"] = key
    now = int(time.time())
    with sqlite3.connect(_path()) as db:
        db.execute("""INSERT INTO visitor_presence(visitor_key,first_seen,last_seen,path)
        VALUES(?,?,?,?) ON CONFLICT(visitor_key) DO UPDATE SET last_seen=excluded.last_seen,path=excluded.path""",
        (key, now, now, request.path[:250]))
        db.execute("DELETE FROM visitor_presence WHERE last_seen < ?", (now-86400,))
    return {"success": True}

def get_operator_overview():
    now = int(time.time())
    with sqlite3.connect(_path()) as db:
        db.row_factory = sqlite3.Row
        online = db.execute("SELECT COUNT(*) n FROM visitor_presence WHERE last_seen >= ?", (now-45,)).fetchone()["n"]
        today = db.execute("SELECT COUNT(*) n FROM visitor_presence WHERE first_seen >= ?", (now-86400,)).fetchone()["n"]
        tables = {r["name"] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        def count(table):
            return db.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0] if table in tables else 0
        return {"visitors_online": online, "visitors_today": today,
                "waifu_characters": count("waifu_characters"),
                "waifu_questions": count("matching_questions"),
                "waifu_matches_saved": count("waifu_match_history"),
                "operator_accounts": count("waifu_operator_accounts")}
