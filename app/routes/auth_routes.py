"""Web routes for admin login/logout -- server-rendered forms, not JSON.

(See api_routes.py for the JSON equivalent, POST /api/login, used by
Postman/programmatic clients.)
"""
from flask import Blueprint, flash, redirect, render_template, request, url_for

from app.auth import is_logged_in, login_admin, logout_admin
from app.models.admin import get_admin_by_username, verify_admin_password

bp = Blueprint("auth", __name__)


@bp.route("/login", methods=["GET", "POST"])
def login():
    if is_logged_in():
        return redirect(url_for("students.list_students"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        admin = get_admin_by_username(username)
        if admin and verify_admin_password(admin, password):
            login_admin(admin["admin_id"], admin["username"])
            return redirect(request.args.get("next") or url_for("students.list_students"))

        flash("Invalid username or password", "error")

    return render_template("login.html")


@bp.route("/logout")
def logout():
    logout_admin()
    flash("Logged out", "success")
    return redirect(url_for("auth.login"))