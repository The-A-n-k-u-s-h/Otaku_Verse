import json
import secrets
from datetime import datetime, timezone
from app.services.waifu_database import get_db

def _now():
    return datetime.now(timezone.utc).isoformat()

def create_profile_session():
    db = get_db()
    match_id = secrets.token_urlsafe(32)
    db.execute(
        "INSERT INTO waifu_profile_sessions(match_id,status,created_at,updated_at) VALUES(?, 'in_progress', ?, ?)",
        (match_id, _now(), _now())
    )
    db.commit()
    return match_id

def get_profile_session(match_id):
    if not match_id:
        return None
    row = get_db().execute(
        "SELECT * FROM waifu_profile_sessions WHERE match_id=?", (match_id,)
    ).fetchone()
    return dict(row) if row else None

def save_answer(match_id, question_id, option_id):
    db = get_db()
    session_row = db.execute(
        "SELECT * FROM waifu_profile_sessions WHERE match_id=? AND status='in_progress'",
        (match_id,)
    ).fetchone()
    if not session_row:
        raise ValueError("Your questionnaire session is missing or has already ended. Start again.")
    question = db.execute(
        "SELECT id, profile_type, trait_key FROM matching_questions WHERE id=? AND status='approved'",
        (question_id,)
    ).fetchone()
    if not question:
        raise ValueError("This question is no longer available.")
    option = db.execute(
        """SELECT o.id, m.score_value FROM question_options o
           JOIN question_trait_mappings m ON m.option_id=o.id
           WHERE o.id=? AND o.question_id=? AND m.trait_key=?""",
        (option_id, question_id, question["trait_key"])
    ).fetchone()
    if not option:
        raise ValueError("Selected answer option does not belong to this question.")
    db.execute(
        """INSERT INTO waifu_profile_answers(match_id,question_id,option_id,profile_type,trait_key,score_value,answered_at)
           VALUES(?,?,?,?,?,?,?)
           ON CONFLICT(match_id,question_id) DO UPDATE SET
             option_id=excluded.option_id, profile_type=excluded.profile_type,
             trait_key=excluded.trait_key, score_value=excluded.score_value,
             answered_at=excluded.answered_at""",
        (match_id, question_id, option_id, question["profile_type"], question["trait_key"],
         option["score_value"], _now())
    )
    db.execute("UPDATE waifu_profile_sessions SET updated_at=? WHERE match_id=?", (_now(), match_id))
    _rebuild_profile_scores(db, match_id)
    db.commit()
    return get_profiles(match_id)

def _rebuild_profile_scores(db, match_id):
    db.execute("DELETE FROM waifu_profile_trait_scores WHERE match_id=?", (match_id,))
    rows = db.execute(
        """SELECT profile_type, trait_key, AVG(score_value) AS average_score, COUNT(*) AS answer_count
           FROM waifu_profile_answers WHERE match_id=?
           GROUP BY profile_type, trait_key""", (match_id,)
    ).fetchall()
    for row in rows:
        db.execute(
            """INSERT INTO waifu_profile_trait_scores
               (match_id,profile_type,trait_key,score_value,answer_count,updated_at)
               VALUES(?,?,?,?,?,?)""",
            (match_id, row["profile_type"], row["trait_key"],
             round(row["average_score"]), row["answer_count"], _now())
        )

def get_profiles(match_id):
    db = get_db()
    rows = db.execute(
        """SELECT profile_type,trait_key,score_value,answer_count
           FROM waifu_profile_trait_scores WHERE match_id=?
           ORDER BY profile_type,trait_key""", (match_id,)
    ).fetchall()
    result = {"personality": {}, "romantic": {}}
    for row in rows:
        result[row["profile_type"]][row["trait_key"]] = {
            "score": row["score_value"], "answer_count": row["answer_count"]
        }
    return result

def get_answered_question_ids(match_id):
    rows = get_db().execute(
        "SELECT question_id FROM waifu_profile_answers WHERE match_id=?", (match_id,)
    ).fetchall()
    return {row["question_id"] for row in rows}

def answer_counts(match_id):
    rows = get_db().execute(
        """SELECT profile_type, COUNT(*) AS total FROM waifu_profile_answers
           WHERE match_id=? GROUP BY profile_type""", (match_id,)
    ).fetchall()
    return {row["profile_type"]: row["total"] for row in rows}

def mark_session_complete(match_id):
    db = get_db()
    db.execute(
        "UPDATE waifu_profile_sessions SET status='completed', updated_at=? WHERE match_id=?",
        (_now(), match_id)
    )
    db.commit()
