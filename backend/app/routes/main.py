import time

from flask import Blueprint, jsonify, render_template, request, session

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def home():
    return render_template("main/home.html")


@main_bp.route("/api/guest/start", methods=["POST"])
def start_guest():
    data = request.get_json(silent=True) or {}
    duration = data.get("duration")

    if duration not in [10, 20, 30]:
        return jsonify({
            "success": False,
            "message": "Choose 10, 20 or 30 minutes."
        }), 400

    expires_at = int(time.time()) + (duration * 60)

    session.clear()
    session.permanent = True
    session["guest_mode"] = True
    session["guest_started_at"] = int(time.time())
    session["guest_expires_at"] = expires_at

    return jsonify({
        "success": True,
        "message": "Guest session started.",
        "expires_at": expires_at,
        "duration": duration
    })


@main_bp.route("/api/guest/status")
def guest_status():
    if not session.get("guest_mode"):
        return jsonify({"active": False})

    expires_at = session.get("guest_expires_at", 0)

    if time.time() >= expires_at:
        session.clear()
        return jsonify({
            "active": False,
            "expired": True
        })

    return jsonify({
        "active": True,
        "expires_at": expires_at
    })


@main_bp.route("/api/guest/end", methods=["POST"])
def end_guest():
    session.clear()

    return jsonify({
        "success": True,
        "message": "Guest session ended."
    })