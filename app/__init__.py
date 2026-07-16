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

    from app.routes.api_routes import bp as api_bp
    from app.routes.auth_routes import bp as auth_bp
    from app.routes.student_routes import bp as students_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(students_bp)
    app.register_blueprint(api_bp)

    return app