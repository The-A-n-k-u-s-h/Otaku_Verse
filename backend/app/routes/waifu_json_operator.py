from flask import Blueprint, jsonify, request, make_response, session
from app.routes.waifu_operator import operator_required
from app.services.waifu_json_bank import build_bank, export_bank, import_bank, bank_path
import os

waifu_json_bp = Blueprint("waifu_json", __name__, url_prefix="/operator/waifu/api/json")

@waifu_json_bp.get("")
@operator_required
def get_json_bank():
    return jsonify({"success": True, "bank": build_bank()})

@waifu_json_bp.get("/status")
@operator_required
def json_sync_status():
    path = bank_path()
    return jsonify({"success": True, "exists": os.path.isfile(path), "path": path,
                    "sync": __import__("flask").current_app.extensions.get("waifu_json_sync", {})})

@waifu_json_bp.post("/sync")
@operator_required
def sync_json_bank():
    data = export_bank()
    return jsonify({"success": True, "message": "JSON bank synchronized.",
                    "question_count": len(data["questions"]), "character_count": len(data["characters"])})

@waifu_json_bp.get("/export")
@operator_required
def download_json_bank():
    data = export_bank()
    response = make_response(jsonify({"success": True, "bank": data}))
    response.headers["Content-Disposition"] = 'attachment; filename="waifu_question_bank.json"'
    return response

@waifu_json_bp.post("/import/preview")
@operator_required
def preview_json_import():
    result = import_bank(request.get_json(silent=True), apply=False)
    return jsonify(result), (200 if result.get("success") else 400)

@waifu_json_bp.post("/import")
@operator_required
def apply_json_import():
    result = import_bank(request.get_json(silent=True), actor=session.get("waifu_operator_name", "operator"), apply=True)
    return jsonify(result), (200 if result.get("success") else 400)
