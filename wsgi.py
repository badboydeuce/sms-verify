# wsgi.py

from app.api.app import app

# Gunicorn will use this
# Example: gunicorn wsgi:app

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
