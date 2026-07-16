"""Admin lookups for authentication.

Passwords are never stored or compared in plaintext -- werkzeug's
check_password_hash re-derives the hash from the attempt and compares
digests, so the real password is never reconstructed or logged.
"""
from werkzeug.security import check_password_hash

from app.db import get_connection


def get_admin_by_username(username):
    """Fetch a single admin row by username, or None if no such admin."""
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT admin_id, username, password_hash FROM admins WHERE username = %s",
            (username,),
        )
        return cursor.fetchone()
    finally:
        conn.close()


def verify_admin_password(admin, password):
    """Check a plaintext password attempt against the admin's stored hash."""
    return check_password_hash(admin["password_hash"], password)