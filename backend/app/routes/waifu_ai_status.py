from flask import Blueprint, jsonify
from app.routes.waifu_operator import operator_required
from app.services.waifu_ai_service import get_provider_status

waifu_ai_status_bp = Blueprint(
    "waifu_ai_status", __name__, url_prefix="/operator/waifu/ai"
)

@waifu_ai_status_bp.get("/providers/status")
@operator_required
def provider_status():
    """Returns provider names/configuration only, never API keys."""
    return jsonify({"success": True, "providers": get_provider_status()})
