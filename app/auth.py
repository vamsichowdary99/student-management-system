"""Session-based authentication: login_required decorator + session helpers.

Server-side sessions (a signed cookie holding just the admin's id/username)
are the simplest correct choice for a Flask+Jinja admin UI -- Flask signs
the cookie using SECRET_KEY, so there's no need to invent or store our own
auth tokens.
"""
from functools import wraps

from flask import jsonify, redirect, request, session, url_for


def login_admin(admin_id, username):
    """Record the logged-in admin's identity in the session."""
    session["admin_id"] = admin_id
    session["username"] = username


def logout_admin():
    session.clear()


def is_logged_in():
    return "admin_id" in session


def login_required(view):
    """Guard a route so only a logged-in admin can reach it.

    Web pages redirect to the login form; JSON API routes get a 401 instead,
    since redirecting a REST/Postman client to an HTML login page would just
    confuse it.
    """

    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if not is_logged_in():
            if request.path.startswith("/api/"):
                return jsonify({"error": "authentication required"}), 401
            return redirect(url_for("auth.login", next=request.path))
        return view(*args, **kwargs)

    return wrapped_view