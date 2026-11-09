from flask import Blueprint, jsonify, render_template, request, session
from app.services.waifu_catalog_service import list_characters, list_questions

character_match_bp = Blueprint("character_match", __name__)

@character_match_bp.get("/character-match")
def character_match_page():
    return render_template("character_match/questionnaire.html")

@character_match_bp.get("/api/waifu/characters")
def public_characters():
    # Only approved characters are visible to public clients.
    result = list_characters(search=request.args.get("q"), approved_only=True,
                             page=request.args.get("page", 1))
    return jsonify({"success": True, **result})

@character_match_bp.get("/api/waifu/questions")
def public_questions():
    # Only approved questions are exposed. Scoring mappings are intentionally
    # not returned to the browser.
    questions = list_questions(approved_only=True)
    safe = []
    for q in questions:
        safe.append({
            "id": q["id"], "prompt": q["prompt"], "category": q["category"],
            "profile_type": q["profile_type"],
            "options": [{"id": o["id"], "text": o["option_text"]} for o in q["options"]]
        })
    return jsonify({"success": True, "items": safe})
