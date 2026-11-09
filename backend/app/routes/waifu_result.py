from flask import Blueprint, jsonify, render_template, session

from app.routes.waifu_history import waifu_history_owner_key
from app.services.waifu_compatibility_service import get_best_waifu_match
from app.services.waifu_explanation_service import get_match_explanation
from app.services.waifu_history_service import save_match_history
from app.services.waifu_profile_service import get_profiles, get_profile_session

waifu_result_bp = Blueprint("waifu_result", __name__)

@waifu_result_bp.get("/character-match/results")
def result_page():
    """Render the result shell. The page loads its private result from the API."""
    return render_template("character_match/results.html")

@waifu_result_bp.get("/api/waifu/result/")
def generate_result():
    match_id = session.get("waifu_match_id")
    if not match_id:
        return jsonify({"success": False, "message": "Please complete the questionnaire first."}), 401

    try:
        profile_session = get_profile_session(match_id)
        if not profile_session:
            return jsonify({"success": False, "message": "Your questionnaire session was not found. Please start again."}), 404
        if profile_session.get("status") != "completed":
            return jsonify({"success": False, "message": "Please answer all required questions before viewing your result."}), 409

        profiles = get_profiles(match_id)
        match_result = get_best_waifu_match(match_id)
        explanation_result = get_match_explanation(match_result, profiles)
        character = match_result["character"]

        history_match_data = {
            "character": {
                "id": character["id"],
                "name": character["name"],
                "anime_title": character["anime_title"],
                "image_url": character.get("image_url", ""),
                "description": character.get("description", "")
            },
            "compatibility": {
                "overall_score": match_result["compatibility_score"],
                "personality_score": match_result["personality_score"],
                "romantic_score": match_result["romantic_score"]
            }
        }
        save_match_history(
            match_id=match_id,
            owner_key=waifu_history_owner_key(),
            match_data=history_match_data,
            explanation=explanation_result["explanation"]
        )

        return jsonify({
            "success": True,
            "result": {
                "character": {
                    "id": character["id"],
                    "name": character["name"],
                    "anime_title": character["anime_title"],
                    "description": character.get("description", ""),
                    "biography": character.get("biography", ""),
                    "image_url": character.get("image_url", "")
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
        return jsonify({"success": False, "message": str(exc)}), 400
