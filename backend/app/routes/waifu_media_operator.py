from flask import Blueprint, jsonify, request, session
from app.services.waifu_media_tools import check_media_url, validate_schedule

waifu_media_operator_bp = Blueprint(
    "waifu_media_operator", __name__, url_prefix="/operator/waifu/api/media"
)

def _require_operator():
    return bool(session.get("waifu_operator") or session.get("operator_id"))

@waifu_media_operator_bp.post("/check")
def check_url():
    if not _require_operator():
        return jsonify({"success": False, "message": "Operator login required."}), 401
    data = request.get_json(silent=True) or {}
    try:
        result = check_media_url(data.get("url", ""), data.get("media_type", "image"))
        return jsonify({"success": True, "result": result})
    except ValueError as exc:
        return jsonify({"success": False, "message": str(exc)}), 400

@waifu_media_operator_bp.post("/validate-schedule")
def validate_schedule_route():
    if not _require_operator():
        return jsonify({"success": False, "message": "Operator login required."}), 401
    data = request.get_json(silent=True) or {}
    try:
        validate_schedule(data.get("start_at"), data.get("end_at"))
        return jsonify({"success": True, "valid": True})
    except (ValueError, TypeError) as exc:
        return jsonify({"success": False, "message": str(exc)}), 400
