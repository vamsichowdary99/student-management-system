"""Database connection helper built on mysql-connector-python.

This project uses raw parameterized SQL (no ORM) throughout, on purpose: it
demonstrates real SQL skill and, more importantly, safe parameter binding
(the %s placeholders mysql-connector fills in) instead of string-formatted
SQL, which is how SQL injection vulnerabilities happen.
"""
import mysql.connector
from flask import current_app


def get_connection():
    """Open a new MySQL connection using the current app's configuration.

    A fresh connection per request -- rather than a shared pool -- is the
    simplest correct choice for a beginner-friendly project, and Gunicorn's
    process/worker model means each request is short-lived anyway.
    """
    return mysql.connector.connect(
        host=current_app.config["DB_HOST"],
        port=current_app.config["DB_PORT"],
        database=current_app.config["DB_NAME"],
        user=current_app.config["DB_USER"],
        password=current_app.config["DB_PASSWORD"],
    )