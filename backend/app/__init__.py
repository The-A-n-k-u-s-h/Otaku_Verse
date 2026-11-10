import os
import time
from datetime import timedelta
from flask import Flask, session

def create_app(test_config=None):
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    app = Flask(
        __name__,
        template_folder=os.path.join(project_root, "frontend", "templates"),
        static_folder=os.path.join(project_root, "frontend", "static"),
        static_url_path="/static",
    )
    app.config.update(
        SECRET_KEY=os.environ.get("SECRET_KEY", "development-only-change-this-key"),
        PERMANENT_SESSION_LIFETIME=timedelta(minutes=30),
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        WAIFU_DATABASE=os.environ.get("WAIFU_DATABASE") or os.path.join(project_root, "instance", "waifu_matching.sqlite3"),
    )
    if test_config:
        app.config.update(test_config)
    if not app.debug and app.config["SECRET_KEY"] == "development-only-change-this-key":
        raise RuntimeError("Set a secure SECRET_KEY before production deployment.")

    from app.services.waifu_database import init_waifu_db
    init_waifu_db(app)

    from app.routes.main import main_bp
    from app.routes.character_match import character_match_bp
    from app.routes.waifu_operator import waifu_operator_bp
    from app.routes.waifu_ai_operator import waifu_ai_operator_bp
    from app.routes.waifu_profile import waifu_profile_bp
    from app.routes.waifu_result import waifu_result_bp
    from app.routes.waifu_history import waifu_history_bp
    from app.routes.operator import operator_bp
    from app.routes.waifu_json_operator import waifu_json_bp
    from app.routes.waifu_ai_status import waifu_ai_status_bp
    from app.routes.waifu_media_operator import waifu_media_operator_bp

    


    app.register_blueprint(main_bp)
    app.register_blueprint(character_match_bp)
    app.register_blueprint(waifu_operator_bp)
    app.register_blueprint(waifu_ai_operator_bp)
    app.register_blueprint(waifu_profile_bp)
    app.register_blueprint(waifu_result_bp)
    app.register_blueprint(waifu_history_bp)
    app.register_blueprint(operator_bp)
    app.register_blueprint(waifu_json_bp)
    app.register_blueprint(waifu_ai_status_bp)
    app.register_blueprint(waifu_media_operator_bp)
    @app.before_request
    def check_guest_expiry():
        if session.get("guest_mode"):
            expires_at = session.get("guest_expires_at", 0)
            if time.time() >= expires_at:
                session.clear()

    return app
