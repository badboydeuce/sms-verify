from flask import Flask

from app.api.routes.numbers import numbers_bp
from app.api.routes.wallet import wallet_bp
from app.api.routes.otp import otp_bp
from app.api.routes.webhook import webhook_bp

from app.core.database import init_db


def create_app():
    app = Flask(__name__)

    # =========================
    # ⚠️ SAFE DB INIT (RUN ONCE)
    # =========================
    try:
        init_db()
    except Exception as e:
        print(f"[DB INIT ERROR] {e}")

    # =========================
    # REGISTER BLUEPRINTS
    # =========================
    app.register_blueprint(numbers_bp, url_prefix="/numbers")
    app.register_blueprint(wallet_bp, url_prefix="/wallet")
    app.register_blueprint(otp_bp, url_prefix="/otp")
    app.register_blueprint(webhook_bp, url_prefix="/webhook")

    # =========================
    # HEALTH CHECK
    # =========================
    @app.route("/")
    def home():
        return {
            "status": "DeuceVerify API running",
            "version": "1.0"
        }

    return app


# Gunicorn entrypoint
app = create_app()