from flask import Flask

from api.routes.health import health_router
from api.routes.wallet import wallet_router
from api.routes.webhook import webhook_router
from api.routes.orders import orders_router

app = Flask(__name__)

app.register_blueprint(health_router)
app.register_blueprint(wallet_router)
app.register_blueprint(webhook_router)
app.register_blueprint(orders_router)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)