"""Central operator portal with master-password and per-feature access codes."""
import hmac
import os
from functools import wraps
from flask import Blueprint, abort, flash, jsonify, redirect, render_template, request, session, url_for
from app.services.operator_audit import FEATURES, init_operator_audit, list_activity, record_activity

operator_bp = Blueprint("operator", __name__, url_prefix="/operator")


def _valid_secret(env_name, supplied):
    expected = os.environ.get(env_name, "")
    return bool(expected and supplied and hmac.compare_digest(str(supplied), expected))


def operator_login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("central_operator_authenticated"):
            return redirect(url_for("operator.login"))
        return view(*args, **kwargs)
    return wrapped


def feature_required(feature):
    def decorator(view):
        @wraps(view)
        @operator_login_required
        def wrapped(*args, **kwargs):
            if session.get("operator_feature") != feature:
                return redirect(url_for("operator.select_feature"))
            return view(*args, **kwargs)
        return wrapped
    return decorator


@operator_bp.record_once
def _setup(state):
    init_operator_audit(state.app)


@operator_bp.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        expected_user = os.environ.get("OPERATOR_USERNAME", "")
        if expected_user and hmac.compare_digest(username, expected_user) and _valid_secret("OPERATOR_MASTER_PASSWORD", password):
            session.clear()
            session["central_operator_authenticated"] = True
            session["central_operator_name"] = username
            session.permanent = True
            return redirect(url_for("operator.select_feature"))
        error = "Invalid operator username or master password. Check your environment settings."
    return render_template("operator/central_login.html", error=error)


@operator_bp.post("/logout")
@operator_login_required
def logout():
    session.pop("central_operator_authenticated", None)
    session.pop("central_operator_name", None)
    session.pop("operator_feature", None)
    session.pop("waifu_operator", None)
    session.pop("waifu_operator_name", None)
    return redirect(url_for("operator.login"))


@operator_bp.get("/")
@operator_login_required
def select_feature():
    return render_template("operator/central_dashboard.html", features=FEATURES,
                           active_feature=session.get("operator_feature"))


@operator_bp.route("/access/<feature>", methods=["GET", "POST"])
@operator_login_required
def feature_access(feature):
    if feature not in FEATURES:
        abort(404)
    error = None
    if request.method == "POST":
        code = request.form.get("access_code", "")
        env_key = "OPERATOR_CODE_" + feature.upper()
        if _valid_secret(env_key, code):
            session["operator_feature"] = feature
            if feature == "waifu":
                session["waifu_operator"] = True
                session["waifu_operator_name"] = session.get("central_operator_name", "operator")
            record_activity(session.get("central_operator_name", "operator"), feature,
                            "access_granted", "Operator opened the feature dashboard.")
            return redirect(url_for("operator.feature_dashboard", feature=feature))
        error = "Incorrect feature access code."
    return render_template("operator/feature_access.html", feature=feature,
                           feature_name=FEATURES[feature], error=error)


@operator_bp.get("/<feature>")
@operator_login_required
def feature_dashboard(feature):
    if feature not in FEATURES:
        abort(404)
    if session.get("operator_feature") != feature:
        return redirect(url_for("operator.feature_access", feature=feature))
    return render_template("operator/feature_dashboard.html", feature=feature,
                           feature_name=FEATURES[feature], activity=list_activity(feature, 30))


@operator_bp.get("/activity")
@operator_login_required
def all_activity():
    return render_template("operator/activity.html", activity=list_activity(limit=250), features=FEATURES)


@operator_bp.post("/api/activity")
@operator_login_required
def add_activity():
    data = request.get_json(silent=True) or {}
    feature = data.get("feature")
    if feature not in FEATURES or session.get("operator_feature") != feature:
        return jsonify({"success": False, "message": "You do not have access to this feature."}), 403
    summary = str(data.get("summary", "")).strip()
    if not summary:
        return jsonify({"success": False, "message": "A change summary is required."}), 400
    try:
        record_activity(session.get("central_operator_name", "operator"), feature,
                        data.get("action", "update"), summary,
                        data.get("before", {}), data.get("after", {}))
    except (TypeError, ValueError) as exc:
        return jsonify({"success": False, "message": str(exc)}), 400
    return jsonify({"success": True, "message": "Change recorded in the activity log."}), 201
