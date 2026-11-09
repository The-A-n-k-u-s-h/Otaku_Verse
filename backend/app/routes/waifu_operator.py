import hmac
import os
from functools import wraps
from flask import Blueprint, current_app, flash, jsonify, redirect, render_template, request, session, url_for
from app.utils.waifu_validation import PERSONALITY_TRAITS, ROMANTIC_TRAITS
from app.services.waifu_catalog_service import (
    list_characters, get_character, create_character, update_character,
    set_character_status, delete_character, list_questions, get_question,
    create_question, update_question, set_question_status, delete_question
)

waifu_operator_bp = Blueprint("waifu_operator", __name__, url_prefix="/operator/waifu")

def operator_required(fn):
    @wraps(fn)
    def wrapped(*args, **kwargs):
        if not session.get("waifu_operator"):
            if request.path.startswith("/api/"):
                return jsonify({"success": False, "message": "Operator login required."}), 401
            return redirect(url_for("waifu_operator.login", next=request.path))
        return fn(*args, **kwargs)
    return wrapped

@waifu_operator_bp.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = os.environ.get("OPERATOR_USERNAME", "")
        password = os.environ.get("OPERATOR_PASSWORD", "")
        supplied_user = request.form.get("username", "")
        supplied_pass = request.form.get("password", "")
        if (username and password and hmac.compare_digest(supplied_user, username)
                and hmac.compare_digest(supplied_pass, password)):
            session.clear()
            session["waifu_operator"] = True
            session["waifu_operator_name"] = supplied_user
            return redirect(request.args.get("next") or url_for("waifu_operator.characters_page"))
        error = "Invalid operator credentials or operator credentials are not configured."
    return render_template("operator/waifu_login.html", error=error)

@waifu_operator_bp.post("/logout")
@operator_required
def logout():
    session.pop("waifu_operator", None)
    session.pop("waifu_operator_name", None)
    return redirect(url_for("waifu_operator.login"))

@waifu_operator_bp.get("/")
@operator_required
def dashboard():
    chars = list_characters()
    questions = list_questions()
    return render_template("operator/waifu_dashboard.html",
        character_total=chars["total"],
        question_total=len(questions),
        pending_characters=sum(x["status"]=="pending_review" for x in chars["items"]),
        pending_questions=sum(x["status"]=="pending_review" for x in questions))

@waifu_operator_bp.get("/characters")
@operator_required
def characters_page():
    data=list_characters(status=request.args.get("status"), search=request.args.get("q"))
    return render_template("operator/waifu_characters.html", characters=data["items"],
                           total=data["total"], status=request.args.get("status",""),
                           query=request.args.get("q",""))

@waifu_operator_bp.get("/characters/new")
@operator_required
def new_character_page():
    return render_template("operator/waifu_character_form.html", character=None, personality_traits=PERSONALITY_TRAITS, romantic_traits=ROMANTIC_TRAITS)

@waifu_operator_bp.get("/characters/<int:character_id>/edit")
@operator_required
def edit_character_page(character_id):
    character=get_character(character_id)
    if not character:
        flash("Character not found.", "error")
        return redirect(url_for("waifu_operator.characters_page"))
    return render_template("operator/waifu_character_form.html", character=character, personality_traits=PERSONALITY_TRAITS, romantic_traits=ROMANTIC_TRAITS)

@waifu_operator_bp.get("/questions")
@operator_required
def questions_page():
    questions=list_questions(status=request.args.get("status"), search=request.args.get("q"))
    return render_template("operator/waifu_questions.html", questions=questions,
                           status=request.args.get("status",""), query=request.args.get("q",""))

@waifu_operator_bp.get("/questions/new")
@operator_required
def new_question_page():
    return render_template("operator/waifu_question_form.html", question=None)

@waifu_operator_bp.get("/questions/<int:question_id>/edit")
@operator_required
def edit_question_page(question_id):
    question=get_question(question_id)
    if not question:
        flash("Question not found.", "error")
        return redirect(url_for("waifu_operator.questions_page"))
    return render_template("operator/waifu_question_form.html", question=question)

@waifu_operator_bp.get("/api/characters")
@operator_required
def api_characters():
    return jsonify({"success": True, **list_characters(status=request.args.get("status"), search=request.args.get("q"))})

@waifu_operator_bp.post("/api/characters")
@operator_required
def api_create_character():
    try:
        item=create_character(request.get_json(force=True), session.get("waifu_operator_name","operator"))
        return jsonify({"success": True, "item": item}), 201
    except (ValueError, TypeError) as exc:
        return jsonify({"success": False, "message": str(exc)}), 400

@waifu_operator_bp.put("/api/characters/<int:character_id>")
@operator_required
def api_update_character(character_id):
    try:
        item=update_character(character_id, request.get_json(force=True))
        if not item: return jsonify({"success":False,"message":"Character not found."}),404
        return jsonify({"success":True,"item":item})
    except (ValueError, TypeError) as exc:
        return jsonify({"success":False,"message":str(exc)}),400

@waifu_operator_bp.post("/api/characters/<int:character_id>/status")
@operator_required
def api_character_status(character_id):
    data=request.get_json(silent=True) or {}
    try:
        ok=set_character_status(character_id,data.get("status",""),session.get("waifu_operator_name","operator"),data.get("reason",""))
        if not ok: return jsonify({"success":False,"message":"Character not found."}),404
        return jsonify({"success":True,"message":"Character status updated."})
    except ValueError as exc:
        return jsonify({"success":False,"message":str(exc)}),400

@waifu_operator_bp.delete("/api/characters/<int:character_id>")
@operator_required
def api_delete_character(character_id):
    if not delete_character(character_id): return jsonify({"success":False,"message":"Character not found."}),404
    return jsonify({"success":True,"message":"Character deleted."})

@waifu_operator_bp.post("/api/questions")
@operator_required
def api_create_question():
    try:
        item=create_question(request.get_json(force=True),session.get("waifu_operator_name","operator"))
        return jsonify({"success":True,"item":item}),201
    except (ValueError, TypeError) as exc:
        return jsonify({"success":False,"message":str(exc)}),400

@waifu_operator_bp.put("/api/questions/<int:question_id>")
@operator_required
def api_update_question(question_id):
    try:
        item=update_question(question_id,request.get_json(force=True))
        if not item: return jsonify({"success":False,"message":"Question not found."}),404
        return jsonify({"success":True,"item":item})
    except (ValueError, TypeError) as exc:
        return jsonify({"success":False,"message":str(exc)}),400

@waifu_operator_bp.post("/api/questions/<int:question_id>/status")
@operator_required
def api_question_status(question_id):
    data=request.get_json(silent=True) or {}
    try:
        ok=set_question_status(question_id,data.get("status",""),session.get("waifu_operator_name","operator"),data.get("reason",""))
        if not ok: return jsonify({"success":False,"message":"Question not found."}),404
        return jsonify({"success":True,"message":"Question status updated."})
    except ValueError as exc:
        return jsonify({"success":False,"message":str(exc)}),400

@waifu_operator_bp.delete("/api/questions/<int:question_id>")
@operator_required
def api_delete_question(question_id):
    if not delete_question(question_id): return jsonify({"success":False,"message":"Question not found."}),404
    return jsonify({"success":True,"message":"Question deleted."})
