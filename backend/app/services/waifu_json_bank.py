"""Editable, automatically synchronized JSON bank for Waifu questions."""
import json
import os
import tempfile
from datetime import datetime, timezone
from flask import current_app
from app.services.waifu_database import get_db

SCHEMA_VERSION = "1.0"

def bank_path():
    configured = current_app.config.get("WAIFU_JSON_PATH")
    return configured or os.path.join(current_app.instance_path, "waifu_question_bank.json")

def build_bank():
    db = get_db()
    questions = []
    rows = db.execute("SELECT * FROM matching_questions ORDER BY display_order, id").fetchall()
    for row in rows:
        q = dict(row)
        answers = []
        options = db.execute(
            "SELECT * FROM question_options WHERE question_id=? ORDER BY display_order, id", (q["id"],)
        ).fetchall()
        for option in options:
            mappings = db.execute(
                "SELECT trait_key, score_value FROM question_trait_mappings WHERE option_id=? ORDER BY trait_key",
                (option["id"],)
            ).fetchall()
            answers.append({
                "answer_id": f"answer_{option['id']}",
                "text": option["option_text"],
                "display_order": option["display_order"],
                "scores": [dict(m) for m in mappings],
            })
        origin = "ai_generated" if str(q.get("created_by", "")).lower().startswith("ai:") else "operator_or_manual"
        q["question_id"] = f"question_{q.pop('id')}"
        q["origin"] = origin
        q["answers"] = answers
        questions.append(q)
    characters = []
    for row in db.execute("SELECT * FROM waifu_characters ORDER BY id").fetchall():
        c = dict(row)
        c["character_id"] = f"character_{c.pop('id')}"
        c["traits"] = {"personality": {}, "romantic": {}}
        for t in db.execute(
            "SELECT profile_type, trait_key, trait_label, score FROM character_traits WHERE character_id=? ORDER BY profile_type, trait_key",
            (row["id"],)
        ).fetchall():
            c["traits"][t["profile_type"]][t["trait_key"]] = {"label": t["trait_label"], "score": t["score"]}
        c["sources"] = [dict(x) for x in db.execute(
            "SELECT source_name AS name, source_url AS url, source_type AS type, notes, verified FROM character_sources WHERE character_id=? ORDER BY id",
            (row["id"],)
        ).fetchall()]
        characters.append(c)
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "characters": characters,
        "questions": questions,
    }

def export_bank():
    data = build_bank()
    destination = bank_path()
    directory = os.path.dirname(os.path.abspath(destination))
    os.makedirs(directory, exist_ok=True)
    fd, temp_path = tempfile.mkstemp(prefix="waifu-bank-", suffix=".json", dir=directory)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(data, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
        os.replace(temp_path, destination)
    finally:
        if os.path.exists(temp_path):
            os.unlink(temp_path)
    current_app.extensions["waifu_json_sync"] = {
        "success": True, "path": destination,
        "last_synced_at": data["generated_at"], "question_count": len(data["questions"]),
        "character_count": len(data["characters"]), "error": None,
    }
    return data

def validate_bank(data):
    errors = []
    if not isinstance(data, dict):
        return ["JSON root must be an object."]
    if data.get("schema_version") != SCHEMA_VERSION:
        errors.append("schema_version must be 1.0.")
    questions = data.get("questions", [])
    characters = data.get("characters", [])
    if not isinstance(questions, list):
        errors.append("questions must be an array.")
        questions = []
    if not isinstance(characters, list):
        errors.append("characters must be an array.")
        characters = []

    seen_questions = set()
    for i, q in enumerate(questions):
        if not isinstance(q, dict):
            errors.append(f"questions[{i}] must be an object.")
            continue
        qid = str(q.get("question_id", "")).strip()
        if not qid:
            errors.append(f"questions[{i}].question_id is required.")
        elif qid in seen_questions:
            errors.append(f"Duplicate question_id: {qid}")
        seen_questions.add(qid)
        if not str(q.get("prompt", "")).strip():
            errors.append(f"questions[{i}].prompt is required.")
        if q.get("profile_type") not in ("personality", "romantic"):
            errors.append(f"questions[{i}].profile_type is invalid.")
        from app.utils.waifu_validation import ALL_TRAITS
        if q.get("trait_key") not in ALL_TRAITS.get(q.get("profile_type"), {}):
            errors.append(f"questions[{i}].trait_key is invalid.")
        answers = q.get("answers")
        if not isinstance(answers, list) or not 2 <= len(answers) <= 8:
            errors.append(f"questions[{i}] must contain between 2 and 8 answers.")
            continue
        for j, answer in enumerate(answers):
            if not isinstance(answer, dict) or not str(answer.get("text", "")).strip():
                errors.append(f"questions[{i}].answers[{j}].text is required.")
                continue
            scores = answer.get("scores", [])
            if not isinstance(scores, list):
                errors.append(f"questions[{i}].answers[{j}].scores must be an array.")
                continue
            for score in scores:
                try:
                    value = int(score.get("score_value"))
                    if not 0 <= value <= 100:
                        raise ValueError()
                except (AttributeError, TypeError, ValueError):
                    errors.append(f"questions[{i}].answers[{j}] has an invalid score_value.")

    seen_characters = set()
    for i, character in enumerate(characters):
        if not isinstance(character, dict):
            errors.append(f"characters[{i}] must be an object.")
            continue
        cid = str(character.get("character_id", "")).strip()
        if not cid:
            errors.append(f"characters[{i}].character_id is required.")
        elif cid in seen_characters:
            errors.append(f"Duplicate character_id: {cid}")
        seen_characters.add(cid)
        if not str(character.get("name", "")).strip():
            errors.append(f"characters[{i}].name is required.")
        if not str(character.get("anime_title", "")).strip():
            errors.append(f"characters[{i}].anime_title is required.")
        traits = character.get("traits", {})
        if not isinstance(traits, dict):
            errors.append(f"characters[{i}].traits must be an object.")
            continue
        from app.utils.waifu_validation import ALL_TRAITS
        for profile_type, values in traits.items():
            if profile_type not in ALL_TRAITS or not isinstance(values, dict):
                errors.append(f"characters[{i}].traits.{profile_type} is invalid.")
                continue
            for key, raw in values.items():
                if key not in ALL_TRAITS[profile_type]:
                    errors.append(f"characters[{i}] has unknown trait {profile_type}.{key}.")
                    continue
                score = raw.get("score") if isinstance(raw, dict) else raw
                try:
                    score = int(score)
                    if not 0 <= score <= 100:
                        raise ValueError()
                except (TypeError, ValueError):
                    errors.append(f"characters[{i}] has invalid score for {profile_type}.{key}.")
        sources = character.get("sources", [])
        if not isinstance(sources, list):
            errors.append(f"characters[{i}].sources must be an array.")
        else:
            for j, source in enumerate(sources):
                if not isinstance(source, dict):
                    errors.append(f"characters[{i}].sources[{j}] must be an object.")
                elif not str(source.get("name", "")).strip() or not str(source.get("url", "")).strip():
                    errors.append(f"characters[{i}].sources[{j}] needs name and url.")
    return errors




def import_bank(data, actor="operator", apply=False):
    from app.services.waifu_catalog_service import (
        create_question,
        list_questions,
        set_question_status,
        create_character,
        list_characters,
        set_character_status,
    )
    from app.utils.waifu_validation import ALL_TRAITS

    errors = validate_bank(data)

    if errors:
        return {
            "success": False,
            "errors": errors
        }

    questions = data.get("questions", [])
    characters = data.get("characters", [])

    if not apply:
        return {
            "success": True,
            "preview": True,
            "question_count": len(questions),
            "character_count": len(characters),
            "message": "JSON validation successful."
        }

    imported_questions = []
    imported_characters = []
    skipped_questions = []
    skipped_characters = []
    import_errors = []

    # ---------------------------------
    # IMPORT QUESTIONS
    # ---------------------------------

    existing_questions = list_questions()

    known_questions = {
        (
            q["prompt"].strip().casefold(),
            q["profile_type"],
            q["trait_key"]
        )
        for q in existing_questions
    }

    for index, q in enumerate(questions):

        try:
            identity = (
                q["prompt"].strip().casefold(),
                q["profile_type"],
                q["trait_key"]
            )

            if identity in known_questions:
                skipped_questions.append(q.get("question_id"))
                continue

            options = []

            for option_index, answer in enumerate(q["answers"]):

                score_item = next(
                    (
                        item for item in answer.get("scores", [])
                        if item.get("trait_key") == q["trait_key"]
                    ),
                    None
                )

                if score_item is None:
                    score_item = (
                        answer.get("scores", [{}])[0]
                        if answer.get("scores")
                        else {}
                    )

                options.append({
                    "text": answer["text"],
                    "score": int(score_item.get("score_value", 50)),
                    "order": int(
                        answer.get("display_order", option_index)
                    )
                })

            payload = {
                "prompt": q["prompt"],
                "category": q.get("category", "Imported"),
                "profile_type": q["profile_type"],
                "trait_key": q["trait_key"],
                "explanation": q.get("explanation", ""),
                "is_required": q.get("is_required", True),
                "display_order": q.get("display_order", 0),
                "options": options
            }

            created = create_question(payload, actor)

            # Move the newly created draft into Pending Review.
            set_question_status(
                created["id"],
                "pending_review",
                actor
            )

            imported_questions.append(created["id"])
            known_questions.add(identity)

        except Exception as exc:
            import_errors.append(
                f"Question {index + 1}: {str(exc)}"
            )

    # ---------------------------------
    # IMPORT CHARACTERS
    # ---------------------------------

    existing_result = list_characters(per_page=100)
    known_characters = {
        (
            item["name"].strip().casefold(),
            item["anime_title"].strip().casefold()
        )
        for item in existing_result["items"]
    }

    # Load remaining pages for duplicate checking.
    total_pages = (
        existing_result["total"] + 99
    ) // 100

    for page in range(2, total_pages + 1):
        page_result = list_characters(
            page=page,
            per_page=100
        )

        for item in page_result["items"]:
            known_characters.add((
                item["name"].strip().casefold(),
                item["anime_title"].strip().casefold()
            ))

    for index, character in enumerate(characters):

        try:
            name = str(character.get("name", "")).strip()
            anime = str(character.get("anime_title", "")).strip()

            identity = (
                name.casefold(),
                anime.casefold()
            )

            if identity in known_characters:
                skipped_characters.append(
                    character.get("character_id")
                )
                continue

            raw_traits = character.get("traits", {})

            traits = {
                "personality": {},
                "romantic": {}
            }

            for profile_type in ("personality", "romantic"):

                for key, value in raw_traits.get(
                    profile_type, {}
                ).items():

                    if isinstance(value, dict):
                        score = value.get("score", 50)
                    else:
                        score = value

                    if key not in ALL_TRAITS[profile_type]:
                        continue

                    traits[profile_type][key] = int(score)

            # The current catalog service accepts HTTP/HTTPS URLs.
            # Local /static URLs are left blank for manual editing.
            image_url = character.get("image_url", "")
            image_source_url = character.get(
                "image_source_url", ""
            )

            if not str(image_url).startswith(("http://", "https://")):
                image_url = ""

            if not str(image_source_url).startswith(("http://", "https://")):
                image_source_url = ""

            sources = []

            for source in character.get("sources", []):
                if not isinstance(source, dict):
                    continue

                source_url = str(source.get("url", "")).strip()

                if not source_url.startswith(("http://", "https://")):
                    continue

                sources.append({
                    "name": source.get("name", "Reference"),
                    "url": source_url,
                    "type": source.get("type", "reference"),
                    "notes": source.get("notes", ""),
                    "verified": bool(source.get("verified", False))
                })

            payload = {
                "name": name,
                "anime_title": anime,
                "aliases": ", ".join(
                    character.get("aliases", [])
                    if isinstance(character.get("aliases"), list)
                    else []
                ),
                "description": character.get("description", ""),
                "biography": character.get("biography", ""),
                "image_url": image_url,
                "image_source_url": image_source_url,
                "traits": traits,
                "sources": sources
            }

            created = create_character(payload, actor)

            # Move the newly created draft into Pending Review.
            set_character_status(
                created["id"],
                "pending_review",
                actor
            )

            imported_characters.append(created["id"])
            known_characters.add(identity)

        except Exception as exc:
            import_errors.append(
                f"Character {index + 1}: {str(exc)}"
            )

    # ---------------------------------
    # FINAL RESPONSE
    # ---------------------------------

    try:
        export_bank()
    except Exception as exc:
        import_errors.append(
            f"JSON synchronization: {str(exc)}"
        )

    return {
        "success": len(import_errors) == 0,
        "imported_question_ids": imported_questions,
        "imported_character_ids": imported_characters,
        "skipped_question_ids": skipped_questions,
        "skipped_character_ids": skipped_characters,
        "question_count": len(imported_questions),
        "character_count": len(imported_characters),
        "errors": import_errors,
        "message": (
            "Imported records are now in Pending Review."
            if not import_errors
            else "Import completed with some errors. Check the errors list."
        )
    }


# def import_bank(data, actor="operator", apply=False):
#     errors = validate_bank(data)
#     if errors:
#         return {"success": False, "errors": errors}
#     questions = data.get("questions", [])
#     characters = data.get("characters", [])
#     if not apply:
#         return {
#             "success": True, "preview": True,
#             "question_count": len(questions), "character_count": len(characters)
#         }

#     from app.services.waifu_catalog_service import (
#         create_character, create_question, list_characters, list_questions
#     )
#     existing_characters = list_characters(per_page=100).get("items", [])
#     known_characters = {
#         (c["name"].strip().casefold(), c["anime_title"].strip().casefold())
#         for c in existing_characters
#     }
#     imported_characters, skipped_characters = [], []
#     for item in characters:
#         identity = (
#             item["name"].strip().casefold(),
#             item["anime_title"].strip().casefold()
#         )
#         if identity in known_characters:
#             skipped_characters.append(item.get("character_id"))
#             continue
#         raw_traits = item.get("traits") or {}
#         traits = {
#             profile: {
#                 key: (value.get("score") if isinstance(value, dict) else value)
#                 for key, value in (raw_traits.get(profile) or {}).items()
#             }
#             for profile in ("personality", "romantic")
#         }
#         payload = {
#             "name": item["name"],
#             "anime_title": item["anime_title"],
#             "aliases": item.get("aliases", ""),
#             "description": item.get("description", ""),
#             "biography": item.get("biography", ""),
#             "image_url": item.get("image_url", ""),
#             "gif_url": item.get("gif_url", ""),
#             "image_source_url": item.get("image_source_url", ""),
#             "traits": traits,
#             "sources": item.get("sources", []),
#         }
#         created = create_character(payload, actor=actor)
#         imported_characters.append(created["id"])
#         known_characters.add(identity)

#     existing_questions = list_questions()
#     known_questions = {
#         (q["prompt"].strip().casefold(), q["profile_type"], q["trait_key"])
#         for q in existing_questions
#     }
#     imported_questions, skipped_questions = [], []
#     for q in questions:
#         identity = (q["prompt"].strip().casefold(), q["profile_type"], q["trait_key"])
#         if identity in known_questions:
#             skipped_questions.append(q.get("question_id"))
#             continue
#         options = []
#         for idx, answer in enumerate(q["answers"]):
#             score_item = next(
#                 (x for x in answer.get("scores", []) if x.get("trait_key") == q["trait_key"]),
#                 None
#             )
#             if score_item is None and answer.get("scores"):
#                 score_item = answer["scores"][0]
#             options.append({
#                 "text": answer["text"],
#                 "score": int(score_item.get("score_value", 50)) if score_item else 50,
#                 "order": int(answer.get("display_order", idx))
#             })
#         payload = {
#             "prompt": q["prompt"],
#             "category": q.get("category", "Imported"),
#             "profile_type": q["profile_type"],
#             "trait_key": q["trait_key"],
#             "explanation": q.get("explanation", ""),
#             "is_required": q.get("is_required", True),
#             "display_order": q.get("display_order", 0),
#             "options": options,
#         }
#         created = create_question(payload, actor)
#         imported_questions.append(created["id"])
#         known_questions.add(identity)

    # export_bank()
    # return {
    #     "success": True,
    #     "imported_character_ids": imported_characters,
    #     "skipped_duplicate_character_ids": skipped_characters,
    #     "imported_question_ids": imported_questions,
    #     "skipped_duplicate_question_ids": skipped_questions,
    #     "message": (
    #         "Imported records are drafts. Add verified sources and media to characters, "
    #         "then submit them for review and approval."
    #     )
    # }
