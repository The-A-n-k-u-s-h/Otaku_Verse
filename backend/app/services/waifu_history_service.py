import json


def _validate_score(value, field):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{field} must be a number.")
    if not 0 <= value <= 100:
        raise ValueError(f"{field} must be between 0 and 100.")
    return round(float(value), 2)


def insert_history_record(db, match_id, owner_key, match_data, explanation):
    """Database-level helper, kept separate so it can be tested without Flask."""
    if not isinstance(match_id, str) or not match_id.strip():
        raise ValueError("A valid match ID is required.")
    if not isinstance(owner_key, str) or not owner_key.strip():
        raise ValueError("A valid history owner is required.")

    character = match_data.get("character") or {}
    scores = match_data.get("compatibility") or {}

    character_id = character.get("id")
    character_name = character.get("name")
    anime_title = character.get("anime_title")

    if not character_id or not character_name or not anime_title:
        raise ValueError("The match must include character ID, name and anime title.")

    overall = _validate_score(scores.get("overall_score"), "overall_score")
    personality = _validate_score(scores.get("personality_score"), "personality_score")
    romantic = _validate_score(scores.get("romantic_score"), "romantic_score")

    snapshot = {
        "character": {
            "id": int(character_id),
            "name": str(character_name),
            "anime_title": str(anime_title),
            "image_url": str(character.get("image_url") or ""),
            "gif_url": str(character.get("gif_url") or ""),
            "description": str(character.get("description") or "")
        },
        "compatibility": {
            "overall_score": overall,
            "personality_score": personality,
            "romantic_score": romantic
        }
    }

    explanation_data = explanation if isinstance(explanation, dict) else {}
    db.execute(
        """
        INSERT INTO waifu_match_history (
            match_id, owner_key, character_id, character_name, anime_title,
            image_url, overall_score, personality_score, romantic_score,
            explanation_json, snapshot_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(match_id) DO UPDATE SET
            owner_key=excluded.owner_key,
            character_id=excluded.character_id,
            character_name=excluded.character_name,
            anime_title=excluded.anime_title,
            image_url=excluded.image_url,
            overall_score=excluded.overall_score,
            personality_score=excluded.personality_score,
            romantic_score=excluded.romantic_score,
            explanation_json=excluded.explanation_json,
            snapshot_json=excluded.snapshot_json,
            updated_at=CURRENT_TIMESTAMP
        """,
        (
            match_id, owner_key, int(character_id), str(character_name),
            str(anime_title), snapshot["character"]["image_url"],
            overall, personality, romantic,
            json.dumps(explanation_data, ensure_ascii=False),
            json.dumps(snapshot, ensure_ascii=False)
        )
    )
    db.commit()
    row = db.execute(
        "SELECT * FROM waifu_match_history WHERE match_id=?", (match_id,)
    ).fetchone()
    return dict(row)


def save_match_history(match_id, owner_key, match_data, explanation):
    from app.services.waifu_database import get_db
    return insert_history_record(
        get_db(), match_id, owner_key, match_data, explanation
    )


def list_match_history(owner_key, limit=50, offset=0):
    if not owner_key:
        return []
    limit = max(1, min(int(limit), 100))
    offset = max(0, int(offset))
    rows = get_db().execute(
        """
        SELECT id, match_id, character_id, character_name, anime_title,
               image_url, overall_score, personality_score, romantic_score,
               created_at
        FROM waifu_match_history
        WHERE owner_key=?
        ORDER BY created_at DESC, id DESC
        LIMIT ? OFFSET ?
        """,
        (owner_key, limit, offset)
    ).fetchall()
    return [dict(row) for row in rows]


def get_history_record(owner_key, history_id):
    row = get_db().execute(
        "SELECT * FROM waifu_match_history WHERE id=? AND owner_key=?",
        (history_id, owner_key)
    ).fetchone()
    if not row:
        return None
    record = dict(row)
    record["snapshot"] = json.loads(record.pop("snapshot_json"))
    record["explanation"] = json.loads(record.pop("explanation_json"))
    return record


def delete_history_record(owner_key, history_id):
    cursor = get_db().execute(
        "DELETE FROM waifu_match_history WHERE id=? AND owner_key=?",
        (history_id, owner_key)
    )
    get_db().commit()
    return cursor.rowcount > 0


def clear_match_history(owner_key):
    cursor = get_db().execute(
        "DELETE FROM waifu_match_history WHERE owner_key=?",
        (owner_key,)
    )
    get_db().commit()
    return cursor.rowcount
