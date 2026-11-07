from datetime import timedelta

from flask import Flask, session
from pathlib import Path
import time


def create_app():
    app = Flask(
        __name__,
        template_folder="../../frontend/templates",
        static_folder="../../frontend/static",
        static_url_path="/static"
    )

    app.config["SECRET_KEY"] = "replace-this-with-a-secret-key"
    app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=30)

    from app.routes.main import main_bp
    app.register_blueprint(main_bp)

    @app.before_request
    def check_guest_expiry():
        if session.get("guest_mode"):
            expires_at = session.get("guest_expires_at", 0)

            if time.time() >= expires_at:
                session.clear()

    return app