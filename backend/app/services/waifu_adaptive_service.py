from app.services.waifu_database import get_db
from app.services.waifu_profile_service import (
    get_answered_question_ids, answer_counts, mark_session_complete
)

def _public_question(row):
    db = get_db()
    options = db.execute(
        "SELECT id, option_text, display_order, image_url, gif_url, audio_url FROM question_options WHERE question_id=? ORDER BY display_order,id",
        (row["id"],)
    ).fetchall()
    return {
        "id": row["id"],
        "prompt": row["prompt"],
        "category": row["category"],
        "profile_type": row["profile_type"],
        "image_url": row["image_url"] if "image_url" in row.keys() else "",
        "gif_url": row["gif_url"] if "gif_url" in row.keys() else "",
        "audio_url": row["audio_url"] if "audio_url" in row.keys() else "",
        "options": [{
            "id": o["id"], "text": o["option_text"],
            "image_url": o["image_url"] or "", "gif_url": o["gif_url"] or "",
            "audio_url": o["audio_url"] or ""
        } for o in options],
    }

def choose_next_question(match_id):
    db = get_db()
    answered = get_answered_question_ids(match_id)
    counts = answer_counts(match_id)
    # First build a queue that balances the two separate profiles.
    # Within each profile, prioritise the trait with the fewest answered questions.
    preferred_profile = "personality" if counts.get("personality", 0) <= counts.get("romantic", 0) else "romantic"
    rows = db.execute(
        """SELECT q.id,q.prompt,q.category,q.profile_type,q.trait_key,q.display_order,q.image_url,q.gif_url,q.audio_url,
                  COUNT(a.question_id) AS answered_trait_count
           FROM matching_questions q
           LEFT JOIN waifu_profile_answers a
             ON a.match_id=? AND a.profile_type=q.profile_type AND a.trait_key=q.trait_key
           WHERE q.status='approved'
             AND (q.scheduled_start_at IS NULL OR q.scheduled_start_at <= CURRENT_TIMESTAMP)
             AND (q.scheduled_end_at IS NULL OR q.scheduled_end_at >= CURRENT_TIMESTAMP)
           GROUP BY q.id
           ORDER BY CASE WHEN q.profile_type=? THEN 0 ELSE 1 END,
                    answered_trait_count ASC, q.display_order ASC, q.id ASC""",
        (match_id, preferred_profile)
    ).fetchall()
    for row in rows:
        if row["id"] in answered:
            continue
        # Never expose score mappings to the browser.
        return _public_question(row)
    mark_session_complete(match_id)
    return None

def get_progress(match_id):
    counts = answer_counts(match_id)
    total = get_db().execute(
        """SELECT COUNT(*) FROM matching_questions WHERE status='approved'
           AND (scheduled_start_at IS NULL OR scheduled_start_at <= CURRENT_TIMESTAMP)
           AND (scheduled_end_at IS NULL OR scheduled_end_at >= CURRENT_TIMESTAMP)"""
    ).fetchone()[0]
    answered = len(get_answered_question_ids(match_id))
    return {
        "answered": answered,
        "available_questions": total,
        "personality_answers": counts.get("personality", 0),
        "romantic_answers": counts.get("romantic", 0),
        "completed": total > 0 and answered >= total,
    }
