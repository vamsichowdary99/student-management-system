"""Local dev entrypoint: `python run.py` boots the app with Flask's built-in
server. Inside containers/production, Gunicorn runs the app instead (see
Dockerfile) -- the built-in server isn't meant to handle real traffic.
"""
from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)