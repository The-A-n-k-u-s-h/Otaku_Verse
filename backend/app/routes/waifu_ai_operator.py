from flask import Blueprint, jsonify, request, session
from app.routes.waifu_operator import operator_required
from app.services.waifu_generation_service import generate_and_save_questions, discover_and_save_characters
from app.services.waifu_ai_service import AIConfigurationError, AIProviderError

waifu_ai_operator_bp = Blueprint("waifu_ai_operator", __name__, url_prefix="/operator/waifu/ai")

@waifu_ai_operator_bp.get("/")
@operator_required
def ai_tools_page():
    from flask import render_template
    return render_template("operator/waifu_ai_tools.html")

def _error(exc):
    if isinstance(exc, AIConfigurationError):
        status = 503
    elif isinstance(exc, AIProviderError):
        status = 502
    elif isinstance(exc, (ValueError, TypeError)):
        status = 400
    else:
        status = 500
    return jsonify({"success": False, "message": str(exc)}), status

@waifu_ai_operator_bp.post("/questions/generate")
@operator_required
def generate_questions():
    data = request.get_json(silent=True) or {}
    try:
        items = generate_and_save_questions(
            topic=str(data.get("topic", "")).strip(),
            profile_type=data.get("profile_type"),
            trait_key=data.get("trait_key"),
            count=max(1, min(8, int(data.get("count", 3)))),
            actor=session.get("waifu_operator_name", "operator"),
        )
        return jsonify({"success": True, "message": f"{len(items)} question drafts saved. Review them before approval.", "items": items}), 201
    except (ValueError, TypeError, AIConfigurationError, AIProviderError) as exc:
        return _error(exc)

@waifu_ai_operator_bp.post("/characters/discover")
@operator_required
def discover_characters():
    data = request.get_json(silent=True) or {}
    try:
        items = discover_and_save_characters(
            anime_title=str(data.get("anime_title", "")).strip(),
            count=max(1, min(8, int(data.get("count", 3)))),
            notes=str(data.get("notes", "")).strip(),
            actor=session.get("waifu_operator_name", "operator"),
        )
        return jsonify({"success": True, "message": f"{len(items)} character drafts saved. Verify all facts, traits, sources and image rights before approval.", "items": items}), 201
    except (ValueError, TypeError, AIConfigurationError, AIProviderError) as exc:
        return _error(exc)
