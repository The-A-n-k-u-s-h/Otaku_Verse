
"""Additive schema migration for Waifu question and answer media and scheduling."""
import sqlite3

def migrate_waifu_media(conn: sqlite3.Connection):
    additions = {
        "waifu_characters": [("gif_url", "TEXT NOT NULL DEFAULT ''")],
        "matching_questions": [
            ("image_url", "TEXT NOT NULL DEFAULT ''"),
            ("gif_url", "TEXT NOT NULL DEFAULT ''"),
            ("audio_url", "TEXT NOT NULL DEFAULT ''"),
            ("image_source_url", "TEXT NOT NULL DEFAULT ''"),
            ("difficulty", "TEXT NOT NULL DEFAULT 'medium'"),
            ("scheduled_start_at", "TEXT"),
            ("scheduled_end_at", "TEXT"),
            ("updated_by", "TEXT"),
        ],
        "question_options": [
            ("image_url", "TEXT NOT NULL DEFAULT ''"),
            ("gif_url", "TEXT NOT NULL DEFAULT ''"),
            ("audio_url", "TEXT NOT NULL DEFAULT ''"),
        ],
    }
    for table, columns in additions.items():
        present = {row[1] for row in conn.execute(f"PRAGMA table_info({table})")}
        for name, declaration in columns:
            if name not in present:
                conn.execute(f"ALTER TABLE {table} ADD COLUMN {name} {declaration}")
    conn.execute("""CREATE TABLE IF NOT EXISTS waifu_json_sync (
        id INTEGER PRIMARY KEY CHECK(id=1),
        version INTEGER NOT NULL DEFAULT 0,
        last_exported_at TEXT,
        last_imported_at TEXT,
        checksum TEXT NOT NULL DEFAULT ''
    )""")
    conn.execute("""CREATE TABLE IF NOT EXISTS waifu_json_revisions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        version INTEGER NOT NULL,
        checksum TEXT NOT NULL,
        snapshot_json TEXT NOT NULL,
        actor TEXT NOT NULL DEFAULT 'system',
        action TEXT NOT NULL,
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    )""")
    conn.execute("""CREATE TABLE IF NOT EXISTS waifu_media_checks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        entity_type TEXT NOT NULL,
        entity_id INTEGER NOT NULL,
        field_name TEXT NOT NULL,
        url TEXT NOT NULL,
        is_working INTEGER NOT NULL,
        status_code INTEGER,
        checked_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(entity_type, entity_id, field_name, url)
    )""")
    conn.commit()
