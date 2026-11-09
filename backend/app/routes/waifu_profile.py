from flask import Blueprint, jsonify, request, session
from app.services.waifu_profile_service import (
    create_profile_session, get_profile_session, save_answer, get_profiles
)
from app.services.waifu_adaptive_service import choose_next_question, get_progress

waifu_profile_bp = Blueprint("waifu_profile", __name__, url_prefix="/api/waifu/profile")

@waifu_profile_bp.post("/start")
def start_profile():
    match_id = create_profile_session()
    session["waifu_match_id"] = match_id
    question = choose_next_question(match_id)
    return jsonify({
        "success": True,
        "match_id": match_id,
        "question": question,
        "progress": get_progress(match_id),
        "message": "Questionnaire started. Personality and romantic preference profiles are tracked separately."
    }), 201

def _current_match():
    match_id = session.get("waifu_match_id")
    record = get_profile_session(match_id)
    if not record:
        return None
    return match_id, record

@waifu_profile_bp.get("/next")
def next_question():
    current = _current_match()
    if not current:
        return jsonify({"success": False, "message": "Start a questionnaire first."}), 401
    match_id, record = current
    if record["status"] != "in_progress":
        return jsonify({"success": True, "question": None, "progress": get_progress(match_id), "completed": True})
    question = choose_next_question(match_id)
    return jsonify({
        "success": True,
        "question": question,
        "progress": get_progress(match_id),
        "completed": question is None
    })

@waifu_profile_bp.post("/answer")
def submit_answer():
    current = _current_match()
    if not current:
        return jsonify({"success": False, "message": "Start a questionnaire first."}), 401
    data = request.get_json(silent=True) or {}
    try:
        question_id = int(data.get("question_id"))
        option_id = int(data.get("option_id"))
        match_id, record = current
        if record["status"] != "in_progress":
            return jsonify({"success": False, "message": "This questionnaire is already complete."}), 409
        profiles = save_answer(match_id, question_id, option_id)
        next_item = choose_next_question(match_id)
        return jsonify({
            "success": True,
            "profiles": profiles,
            "next_question": next_item,
            "progress": get_progress(match_id),
            "completed": next_item is None
        })
    except (TypeError, ValueError) as exc:
        return jsonify({"success": False, "message": str(exc)}), 400

@waifu_profile_bp.get("/profiles")
def profile_preview():
    current = _current_match()
    if not current:
        return jsonify({"success": False, "message": "Start a questionnaire first."}), 401
    match_id, record = current
    return jsonify({
        "success": True,
        "profiles": get_profiles(match_id),
        "progress": get_progress(match_id)
    })
