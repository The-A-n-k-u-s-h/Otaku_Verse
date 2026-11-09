HISTORY_SCHEMA = """
CREATE TABLE IF NOT EXISTS waifu_match_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    match_id TEXT NOT NULL UNIQUE,
    owner_key TEXT NOT NULL,
    character_id INTEGER NOT NULL,
    character_name TEXT NOT NULL,
    anime_title TEXT NOT NULL,
    image_url TEXT NOT NULL DEFAULT '',
    overall_score REAL NOT NULL CHECK(overall_score >= 0 AND overall_score <= 100),
    personality_score REAL NOT NULL CHECK(personality_score >= 0 AND personality_score <= 100),
    romantic_score REAL NOT NULL CHECK(romantic_score >= 0 AND romantic_score <= 100),
    explanation_json TEXT NOT NULL DEFAULT '{}',
    snapshot_json TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_waifu_history_owner_date
ON waifu_match_history(owner_key, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_waifu_history_character
ON waifu_match_history(character_id);
"""
