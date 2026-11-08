
import os
import time
from datetime import timedelta

from flask import Flask, session


def create_app():
    project_root = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..")
    )

    app = Flask(
        __name__,
        template_folder=os.path.join(
            project_root, "frontend", "templates"
        ),
        static_folder=os.path.join(
            project_root, "frontend", "static"
        ),
        static_url_path="/static",
    )

    app.config.update(
        SECRET_KEY=os.environ.get(
            "SECRET_KEY", "development-only-change-this-key"
        ),
        PERMANENT_SESSION_LIFETIME=timedelta(minutes=30),
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
    )

    if not app.debug and app.config["SECRET_KEY"] == "development-only-change-this-key":
        raise RuntimeError("Set a secure SECRET_KEY before production deployment.")

    from app.routes.main import main_bp
    app.register_blueprint(main_bp)

    @app.before_request
    def check_guest_expiry():
        if session.get("guest_mode"):
            expires_at = session.get("guest_expires_at", 0)

            if time.time() >= expires_at:
                session.clear()

    return app
