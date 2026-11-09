
from app.services.waifu_database import get_db
from app.services.waifu_profile_service import get_profiles


def calculate_profile_similarity(user_traits, character_traits):
    """
    Compare user trait scores with character trait scores.
    A smaller difference means a better compatibility score.
    """
    common_traits = set(user_traits.keys()) & set(character_traits.keys())

    if not common_traits:
        return None

    total_similarity = 0

    for trait in common_traits:
        user_score = user_traits[trait]["score"]
        character_score = character_traits[trait]["score"]

        difference = abs(user_score - character_score)
        similarity = 100 - difference

        total_similarity += similarity

    return round(total_similarity / len(common_traits), 2)


def calculate_compatibility(user_profiles, character):
    personality_score = calculate_profile_similarity(
        user_profiles["personality"],
        character["traits"]["personality"]
    )

    romantic_score = calculate_profile_similarity(
        user_profiles["romantic"],
        character["traits"]["romantic"]
    )

    # Both profiles are required for a reliable match.
    if personality_score is None or romantic_score is None:
        return None

    # Romantic preferences receive slightly more weight.
    final_score = (
        personality_score * 0.40
        + romantic_score * 0.60
    )

    return {
        "personality_score": round(personality_score, 2),
        "romantic_score": round(romantic_score, 2),
        "compatibility_score": round(final_score, 2)
    }


def get_best_waifu_match(match_id):
    """
    Find the highest compatibility character from the
    approved character database.
    """
    user_profiles = get_profiles(match_id)

    if not user_profiles["personality"]:
        raise ValueError("Your personality profile is incomplete.")

    if not user_profiles["romantic"]:
        raise ValueError("Your romantic preference profile is incomplete.")

    db = get_db()

    characters = db.execute("""
        SELECT id
        FROM waifu_characters
        WHERE status = 'approved'
          AND verification_status = 'verified'
        ORDER BY id
    """).fetchall()

    if not characters:
        raise ValueError("No approved characters are available yet.")

    results = []

    for row in characters:
        character_id = row["id"]

        character_row = db.execute("""
            SELECT *
            FROM waifu_characters
            WHERE id = ?
        """, (character_id,)).fetchone()

        character = dict(character_row)

        trait_rows = db.execute("""
            SELECT profile_type, trait_key, trait_label, score
            FROM character_traits
            WHERE character_id = ?
        """, (character_id,)).fetchall()

        character["traits"] = {
            "personality": {},
            "romantic": {}
        }

        for trait in trait_rows:
            character["traits"][trait["profile_type"]][trait["trait_key"]] = {
                "label": trait["trait_label"],
                "score": trait["score"]
            }

        scores = calculate_compatibility(
            user_profiles,
            character
        )

        if scores is None:
            continue

        results.append({
            "character": character,
            **scores
        })

    if not results:
        raise ValueError(
            "No characters have enough matching trait information."
        )

    # Highest compatibility first.
    results.sort(
        key=lambda item: item["compatibility_score"],
        reverse=True
    )

    return results[0]
