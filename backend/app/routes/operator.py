"""Super Operator portal and five isolated feature operator logins."""
import hmac, os
from functools import wraps
from flask import Blueprint, abort, flash, jsonify, redirect, render_template, request, session, url_for
from app.services.operator_audit import FEATURES, init_operator_audit, list_activity, record_activity

operator_bp = Blueprint("operator", __name__, url_prefix="/operator")

def _same(expected, supplied):
    return bool(expected and supplied and hmac.compare_digest(str(expected), str(supplied)))

def _feature_login(feature, username, password):
    prefix = "OPERATOR_" + feature.upper()
    return _same(os.getenv(prefix + "_USERNAME", "").strip(), username) and _same(os.getenv(prefix + "_PASSWORD", ""), password)

def operator_login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("central_operator_authenticated"):
            return redirect(url_for("operator.login"))
        return view(*args, **kwargs)
    return wrapped

def super_operator_required(view):
    @wraps(view)
    @operator_login_required
    def wrapped(*args, **kwargs):
        if not session.get("is_super_operator"):
            abort(403)
        return view(*args, **kwargs)
    return wrapped

@operator_bp.record_once
def _setup(state):
    init_operator_audit(state.app)
    from app.services.operator_dashboard_metrics import init_operator_metrics
    init_operator_metrics(state.app)

@operator_bp.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        # Accept both the current SUPER_OPERATOR_* names and the legacy
        # OPERATOR_USERNAME / OPERATOR_MASTER_PASSWORD names used by older .env files.
        super_username = os.getenv("SUPER_OPERATOR_USERNAME", "").strip() or os.getenv("OPERATOR_USERNAME", "").strip()
        super_password = os.getenv("SUPER_OPERATOR_PASSWORD", "") or os.getenv("OPERATOR_MASTER_PASSWORD", "") or os.getenv("OPERATOR_PASSWORD", "")
        if _same(super_username, username) and _same(super_password, password):
            session.clear()
            session.update({"central_operator_authenticated": True, "central_operator_name": username, "is_super_operator": True,
                            "waifu_operator": True, "waifu_operator_name": username, "waifu_operator_role": "super_admin"})
            session.permanent = True
            return redirect(url_for("operator.select_feature"))
        for feature in FEATURES:
            if _feature_login(feature, username, password):
                session.clear()
                session.update({"central_operator_authenticated": True, "central_operator_name": username, "is_super_operator": False, "operator_feature": feature})
                if feature == "waifu":
                    session.update({"waifu_operator": True, "waifu_operator_name": username, "waifu_operator_role": "super_admin"})
                session.permanent = True
                record_activity(username, feature, "login", "Feature operator signed in.")
                return redirect(url_for("operator.feature_dashboard", feature=feature))
        error = "Invalid operator credentials. Check the username and password assigned to your account."
    return render_template("operator/central_login.html", error=error)

@operator_bp.post("/logout")
@operator_login_required
def logout():
    feature = session.get("operator_feature")
    username = session.get("central_operator_name", "operator")
    if feature:
        record_activity(username, feature, "logout", "Feature operator signed out.")
    session.clear()
    return redirect(url_for("operator.login"))

@operator_bp.get("/")
@super_operator_required
def select_feature():
    return render_template("operator/central_dashboard.html", features=FEATURES, active_feature=None)

@operator_bp.route("/access/<feature>", methods=["GET", "POST"])
@operator_login_required
def feature_access(feature):
    if feature not in FEATURES:
        abort(404)
    if not session.get("is_super_operator") and session.get("operator_feature") != feature:
        abort(403)
    return redirect(url_for("operator.feature_dashboard", feature=feature))

@operator_bp.get("/<feature>")
@operator_login_required
def feature_dashboard(feature):
    if feature not in FEATURES:
        abort(404)
    if not session.get("is_super_operator") and session.get("operator_feature") != feature:
        abort(403)
    return render_template("operator/feature_dashboard.html", feature=feature, feature_name=FEATURES[feature], activity=list_activity(feature, 30))

@operator_bp.get("/activity")
@super_operator_required
def all_activity():
    return render_template("operator/activity.html", activity=list_activity(limit=250), features=FEATURES)

@operator_bp.post("/api/activity")
@operator_login_required
def add_activity():
    data = request.get_json(silent=True) or {}
    feature = data.get("feature")
    if feature not in FEATURES or (not session.get("is_super_operator") and session.get("operator_feature") != feature):
        return jsonify({"success": False, "message": "You do not have access to this feature."}), 403
    summary = str(data.get("summary", "")).strip()
    if not summary:
        return jsonify({"success": False, "message": "A change summary is required."}), 400
    try:
        record_activity(session.get("central_operator_name", "operator"), feature, data.get("action", "update"), summary, data.get("before", {}), data.get("after", {}))
    except (TypeError, ValueError) as exc:
        return jsonify({"success": False, "message": str(exc)}), 400
    return jsonify({"success": True, "message": "Change recorded."}), 201

@operator_bp.post("/api/visitor-heartbeat")
def visitor_heartbeat():
    from app.services.operator_dashboard_metrics import heartbeat
    return jsonify(heartbeat())

@operator_bp.get("/api/overview")
@super_operator_required
def overview_api():
    from app.services.operator_dashboard_metrics import get_operator_overview
    return jsonify({"success": True, "overview": get_operator_overview()})
