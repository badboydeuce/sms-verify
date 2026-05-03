# app/main.py

from flask import Flask
from app.routes.numbers import numbers_bp
from app.routes.otp import otp_bp


def create_app():
    app = Flask(__name__)

    # Register routes
    app.register_blueprint(numbers_bp, url_prefix="/numbers")
    app.register_blueprint(otp_bp, url_prefix="/otp")

    @app.route("/")
    def home():
        return {"status": "API running"}

    return app


# This is what Gunicorn uses
app = create_app()