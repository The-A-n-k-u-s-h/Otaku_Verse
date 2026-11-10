import secrets
from flask import Blueprint, jsonify, render_template, request, session

from app.services.waifu_history_service import (
    list_match_history,
    get_history_record,
    delete_history_record,
    clear_match_history
)

waifu_history_bp = Blueprint("waifu_history", __name__)



@waifu_history_bp.get("/character-match/history")
def history_page():
    return render_template("character_match/history.html")



def waifu_history_owner_key():
    # Keep a stable guest owner key in the signed Flask session.
    # Logged-in users are scoped to their account ID.
    user_id = session.get("user_id")
    if user_id is not None:
        return f"user:{user_id}"

    guest_key = session.get("waifu_history_owner")
    if not guest_key:
        guest_key = secrets.token_urlsafe(32)
        session["waifu_history_owner"] = guest_key
    return f"guest:{guest_key}"


@waifu_history_bp.get("/api/waifu/history/")
def history_list():
    try:
        limit = max(1, min(request.args.get("limit", 50, type=int) or 50, 100))
        offset = max(0, request.args.get("offset", 0, type=int) or 0)
        records = list_match_history(
            waifu_history_owner_key(), limit=limit, offset=offset
        )
        return jsonify({"success": True, "history": records})
    except (TypeError, ValueError):
        return jsonify({"success": False, "message": "Invalid pagination values."}), 400


@waifu_history_bp.get("/api/waifu/history/<int:history_id>")
def history_detail(history_id):
    record = get_history_record(waifu_history_owner_key(), history_id)
    if not record:
        return jsonify({"success": False, "message": "History record not found."}), 404
    return jsonify({"success": True, "record": record})


@waifu_history_bp.delete("/api/waifu/history/<int:history_id>")
def history_delete(history_id):
    deleted = delete_history_record(waifu_history_owner_key(), history_id)
    if not deleted:
        return jsonify({"success": False, "message": "History record not found."}), 404
    return jsonify({"success": True, "message": "History record deleted."})


@waifu_history_bp.delete("/api/waifu/history/")
def history_clear():
    deleted_count = clear_match_history(waifu_history_owner_key())
    return jsonify({
        "success": True,
        "deleted_count": deleted_count,
        "message": "Match history cleared."
    })
