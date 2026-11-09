PROFILE_SCHEMA = """
CREATE TABLE IF NOT EXISTS waifu_profile_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    match_id TEXT NOT NULL UNIQUE,
    status TEXT NOT NULL DEFAULT 'in_progress'
        CHECK(status IN ('in_progress','completed','abandoned')),
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS waifu_profile_answers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    match_id TEXT NOT NULL REFERENCES waifu_profile_sessions(match_id) ON DELETE CASCADE,
    question_id INTEGER NOT NULL REFERENCES matching_questions(id) ON DELETE RESTRICT,
    option_id INTEGER NOT NULL REFERENCES question_options(id) ON DELETE RESTRICT,
    profile_type TEXT NOT NULL CHECK(profile_type IN ('personality','romantic')),
    trait_key TEXT NOT NULL,
    score_value INTEGER NOT NULL CHECK(score_value BETWEEN 0 AND 100),
    answered_at TEXT NOT NULL,
    UNIQUE(match_id, question_id)
);

CREATE TABLE IF NOT EXISTS waifu_profile_trait_scores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    match_id TEXT NOT NULL REFERENCES waifu_profile_sessions(match_id) ON DELETE CASCADE,
    profile_type TEXT NOT NULL CHECK(profile_type IN ('personality','romantic')),
    trait_key TEXT NOT NULL,
    score_value INTEGER NOT NULL CHECK(score_value BETWEEN 0 AND 100),
    answer_count INTEGER NOT NULL DEFAULT 0,
    updated_at TEXT NOT NULL,
    UNIQUE(match_id, profile_type, trait_key)
);

CREATE INDEX IF NOT EXISTS idx_waifu_answers_match ON waifu_profile_answers(match_id);
CREATE INDEX IF NOT EXISTS idx_waifu_answers_question ON waifu_profile_answers(question_id);
CREATE INDEX IF NOT EXISTS idx_waifu_profile_scores_match ON waifu_profile_trait_scores(match_id);
"""
