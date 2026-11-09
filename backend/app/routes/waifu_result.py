
from flask import Blueprint, jsonify, session
from app.services.waifu_history_service import save_match_history

from app.services.waifu_profile_service import get_profiles
from app.services.waifu_compatibility_service import (
    get_best_waifu_match
)
from app.services.waifu_explanation_service import (
    get_match_explanation
)



waifu_result_bp = Blueprint(
    "waifu_result",
    __name__,
    url_prefix="/api/waifu/result"
)


@waifu_result_bp.get("/")
def generate_result():

    match_id = session.get("waifu_match_id")

    if not match_id:
        return jsonify({
            "success": False,
            "message": "Please complete the questionnaire first."
        }), 401

    try:
        profiles = get_profiles(match_id)

        # Module 7: Calculate the best character match.
        match_result = get_best_waifu_match(match_id)

        # Module 8: Generate the personalised explanation.
        explanation_result = get_match_explanation(
            match_result,
            profiles
        )

        save_match_history(
    match_id=match_id,
    owner_key=waifu_history_owner_key(),
    match_data={
        "character": {
            "id": character["id"],
            "name": character["name"],
            "anime_title": character["anime_title"],
            "image_url": character.get("image_url", ""),
            "description": character.get("description", "")
        },
        "compatibility": {
            "overall_score": match["compatibility_score"],
            "personality_score": match["personality_score"],
            "romantic_score": match["romantic_score"]
        }
    },
    explanation=explanation_result["explanation"]
)

        character = match_result["character"]

        return jsonify({
            "success": True,
            "result": {
                "character": {
                    "id": character["id"],
                    "name": character["name"],
                    "anime_title": character["anime_title"],
                    "description": character["description"],
                    "biography": character["biography"],
                    "image_url": character["image_url"]
                },
                "compatibility": {
                    "overall": match_result["compatibility_score"],
                    "personality": match_result["personality_score"],
                    "romantic": match_result["romantic_score"]
                },
                "explanation": explanation_result["explanation"],
                "explanation_source": explanation_result["source"]
            }
        })

    except ValueError as exc:
        return jsonify({
            "success": False,
            "message": str(exc)
        }), 400
