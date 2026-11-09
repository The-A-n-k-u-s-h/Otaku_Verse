from app.services.waifu_ai_service import generate_question_drafts, discover_character_candidates
from app.services.waifu_catalog_service import create_question, create_character
from app.utils.waifu_validation import ALL_TRAITS

def generate_and_save_questions(topic, profile_type, trait_key, count, actor):
    if profile_type not in ALL_TRAITS or trait_key not in ALL_TRAITS[profile_type]:
        raise ValueError("Select a valid profile type and trait.")
    drafts = generate_question_drafts(topic, profile_type, trait_key, count)
    saved = []
    for draft in drafts:
        draft["profile_type"] = profile_type
        draft["trait_key"] = trait_key
        draft.setdefault("category", topic[:80] or "AI generated")
        draft.setdefault("explanation", "AI-generated draft. Operator must review wording and scoring.")
        draft.setdefault("is_required", False)
        draft.setdefault("options", [])
        if len(draft["options"]) < 2:
            continue
        saved.append(create_question(draft, actor))
    if not saved:
        raise ValueError("AI drafts did not contain valid questions with at least two options.")
    return saved

def discover_and_save_characters(anime_title, count, notes, actor):
    candidates = discover_character_candidates(anime_title, count, notes)
    saved = []
    for candidate in candidates:
        personality = candidate.get("personality_traits") or {}
        romantic = candidate.get("romantic_traits") or {}
        traits = {
            "personality": {k: int(v) for k, v in personality.items()},
            "romantic": {k: int(v) for k, v in romantic.items()},
        }
        sources = []
        for source in candidate.get("source_suggestions", []):
            url = str(source.get("url") or "").strip()
            # AI-suggested URLs are explicitly unverified and must be checked by an operator.
            if url.startswith(("https://", "http://")):
                sources.append({
                    "name": source.get("name") or "AI suggested source",
                    "url": url, "type": "AI suggestion",
                    "notes": (source.get("notes") or "AI-suggested. Verify this source manually.")[:1000],
                    "verified": False,
                })
        payload = {
            "name": candidate.get("name", ""),
            "anime_title": candidate.get("anime_title") or anime_title,
            "aliases": candidate.get("aliases", ""),
            "description": candidate.get("description", ""),
            "biography": candidate.get("biography", ""),
            "image_url": candidate.get("image_url", ""),
            "image_source_url": candidate.get("image_source_url", ""),
            "traits": traits,
            "sources": sources,
        }
        # create_character always saves as draft. No AI-discovered item is auto-approved.
        saved.append(create_character(payload, actor))
    return saved
