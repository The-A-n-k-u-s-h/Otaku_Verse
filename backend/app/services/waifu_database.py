import os
import sqlite3
from contextlib import contextmanager
from flask import current_app, g
from app.services.waifu_profile_schema import PROFILE_SCHEMA
from app.services.waifu_history_schema import HISTORY_SCHEMA



SCHEMA = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS waifu_characters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    slug TEXT NOT NULL UNIQUE,
    anime_title TEXT NOT NULL,
    aliases TEXT NOT NULL DEFAULT '',
    description TEXT NOT NULL DEFAULT '',
    biography TEXT NOT NULL DEFAULT '',
    image_url TEXT NOT NULL DEFAULT '',
    image_source_url TEXT NOT NULL DEFAULT '',
    status TEXT NOT NULL DEFAULT 'draft'
        CHECK(status IN ('draft','pending_review','approved','rejected','inactive')),
    verification_status TEXT NOT NULL DEFAULT 'unverified'
        CHECK(verification_status IN ('unverified','partially_verified','verified')),
    created_by TEXT NOT NULL DEFAULT 'operator',
    reviewed_by TEXT,
    reviewed_at TEXT,
    rejection_reason TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS character_traits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    character_id INTEGER NOT NULL REFERENCES waifu_characters(id) ON DELETE CASCADE,
    profile_type TEXT NOT NULL CHECK(profile_type IN ('personality','romantic')),
    trait_key TEXT NOT NULL,
    trait_label TEXT NOT NULL,
    score INTEGER NOT NULL CHECK(score BETWEEN 0 AND 100),
    UNIQUE(character_id, profile_type, trait_key)
);

CREATE TABLE IF NOT EXISTS character_sources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    character_id INTEGER NOT NULL REFERENCES waifu_characters(id) ON DELETE CASCADE,
    source_name TEXT NOT NULL,
    source_url TEXT NOT NULL,
    source_type TEXT NOT NULL DEFAULT 'reference',
    notes TEXT NOT NULL DEFAULT '',
    verified INTEGER NOT NULL DEFAULT 0 CHECK(verified IN (0,1)),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS matching_questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    prompt TEXT NOT NULL,
    category TEXT NOT NULL,
    profile_type TEXT NOT NULL CHECK(profile_type IN ('personality','romantic')),
    trait_key TEXT NOT NULL,
    explanation TEXT NOT NULL DEFAULT '',
    status TEXT NOT NULL DEFAULT 'draft'
        CHECK(status IN ('draft','pending_review','approved','rejected','inactive')),
    is_required INTEGER NOT NULL DEFAULT 1 CHECK(is_required IN (0,1)),
    display_order INTEGER NOT NULL DEFAULT 0,
    created_by TEXT NOT NULL DEFAULT 'operator',
    reviewed_by TEXT,
    reviewed_at TEXT,
    rejection_reason TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS question_options (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question_id INTEGER NOT NULL REFERENCES matching_questions(id) ON DELETE CASCADE,
    option_text TEXT NOT NULL,
    display_order INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS question_trait_mappings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    option_id INTEGER NOT NULL REFERENCES question_options(id) ON DELETE CASCADE,
    trait_key TEXT NOT NULL,
    score_value INTEGER NOT NULL CHECK(score_value BETWEEN 0 AND 100),
    UNIQUE(option_id, trait_key)
);

CREATE INDEX IF NOT EXISTS idx_character_status ON waifu_characters(status);
CREATE INDEX IF NOT EXISTS idx_question_status ON matching_questions(status);
CREATE INDEX IF NOT EXISTS idx_character_traits_character ON character_traits(character_id);
CREATE INDEX IF NOT EXISTS idx_question_options_question ON question_options(question_id);
"""

def database_path():
    return current_app.config.get("WAIFU_DATABASE") or os.path.join(current_app.instance_path, "waifu_matching.sqlite3")

def get_db():
    if "waifu_db" not in g:
        path = database_path()
        os.makedirs(os.path.dirname(path), exist_ok=True)
        conn = sqlite3.connect(path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        g.waifu_db = conn
    return g.waifu_db

def close_db(_error=None):
    conn = g.pop("waifu_db", None)
    if conn is not None:
        conn.close()

def init_waifu_db(app):
    os.makedirs(app.instance_path, exist_ok=True)
    path = app.config.get("WAIFU_DATABASE") or os.path.join(app.instance_path, "waifu_matching.sqlite3")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    conn = sqlite3.connect(path)
    conn.executescript(SCHEMA)
    conn.executescript(PROFILE_SCHEMA)
    conn.executescript(HISTORY_SCHEMA)
    from app.services.waifu_media_schema import migrate_waifu_media
    migrate_waifu_media(conn)
    from app.services.operator_accounts_schema import migrate_operator_accounts
    migrate_operator_accounts(conn)
    conn.commit()
    conn.close()
    app.teardown_appcontext(close_db)
