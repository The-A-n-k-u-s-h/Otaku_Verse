"""Audit log storage for the five OtakuVerse feature operators."""
import json
from datetime import datetime, timezone
from flask import current_app
import sqlite3
import os

FEATURES = {
    "recommendations": "Anime Recommendations",
    "quiz": "Anime Quiz",
    "waifu": "Waifu / Character Match",
    "hot_takes": "Anime Hot Takes",
    "discussions": "Anime Discussions",
}


def _db_path():
    configured = current_app.config.get("WAIFU_DATABASE")
    if configured:
        return configured
    return os.path.join(current_app.instance_path, "waifu_matching.sqlite3")


def init_operator_audit(app):
    path = app.config.get("WAIFU_DATABASE") or os.path.join(app.instance_path, "waifu_matching.sqlite3")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with sqlite3.connect(path) as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS operator_activity_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                operator_username TEXT NOT NULL,
                feature_key TEXT NOT NULL,
                action TEXT NOT NULL,
                summary TEXT NOT NULL,
                before_data TEXT NOT NULL DEFAULT '{}',
                after_data TEXT NOT NULL DEFAULT '{}',
                created_at TEXT NOT NULL
            )
        """)
        db.execute("CREATE INDEX IF NOT EXISTS idx_operator_activity_feature ON operator_activity_log(feature_key, created_at DESC)")


def record_activity(username, feature_key, action, summary, before_data=None, after_data=None):
    if feature_key not in FEATURES:
        raise ValueError("Unknown operator feature.")
    action = str(action or "update").strip()[:40]
    summary = str(summary or "Change recorded.").strip()[:500]
    before_json = json.dumps(before_data or {}, ensure_ascii=False)[:10000]
    after_json = json.dumps(after_data or {}, ensure_ascii=False)[:10000]
    with sqlite3.connect(_db_path()) as db:
        db.execute("""
            INSERT INTO operator_activity_log
            (operator_username, feature_key, action, summary, before_data, after_data, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (str(username)[:100], feature_key, action, summary, before_json, after_json,
              datetime.now(timezone.utc).isoformat()))


def list_activity(feature_key=None, limit=100):
    limit = max(1, min(int(limit), 250))
    with sqlite3.connect(_db_path()) as db:
        db.row_factory = sqlite3.Row
        if feature_key in FEATURES:
            rows = db.execute("SELECT * FROM operator_activity_log WHERE feature_key=? ORDER BY id DESC LIMIT ?", (feature_key, limit)).fetchall()
        else:
            rows = db.execute("SELECT * FROM operator_activity_log ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
    result = []
    for row in rows:
        item = dict(row)
        for field in ("before_data", "after_data"):
            try:
                item[field] = json.loads(item[field])
            except (TypeError, json.JSONDecodeError):
                item[field] = {}
        result.append(item)
    return result
