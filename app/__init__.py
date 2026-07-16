"""Flask application factory.

A factory function (create_app()) is used instead of a bare module-level
`app = Flask(__name__)` so tests can spin up isolated app instances with
their own config, and so routes/blueprints can import `app` without
circular-import issues.
"""
from flask import Flask

from app.config import Config


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Blueprints (auth, student web pages, JSON API) are registered here
    # once they exist -- see app/routes/*.

    return app