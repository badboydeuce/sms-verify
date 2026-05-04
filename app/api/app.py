# app/api/app.py

from flask import Flask
from app.api.routes.numbers import numbers_bp
from app.api.routes.wallet import wallet_bp
from app.api.routes.otp import otp_bp
from app.api.routes.webhook import webhook_bp
from app.core.database import init_db

from app.api.routes.wallet import wallet_bp

app.register_blueprint(wallet_bp, url_prefix="/wallet")


def create_app():
    app = Flask(__name__)

    # Initialize DB
    init_db()

    # Register Blueprints
    app.register_blueprint(numbers_bp, url_prefix="/numbers")
    app.register_blueprint(wallet_bp, url_prefix="/wallet")
    app.register_blueprint(otp_bp, url_prefix="/otp")
    app.register_blueprint(webhook_bp, url_prefix="/webhook")

    @app.route("/")
    def home():
        return {"status": "DeuceVerify API running"}

    return app


# Gunicorn entrypoint
app = create_app()
