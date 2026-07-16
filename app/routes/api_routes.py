"""JSON REST API for Postman / programmatic clients.

Reuses the same session-based auth as the web UI (POST /api/login sets the
session cookie), so login_required's 401-JSON branch protects these routes
exactly like the web routes, just without an HTML redirect.
"""
from flask import Blueprint, jsonify, request
from mysql.connector import IntegrityError
from mysql.connector.errorcode import ER_DUP_ENTRY, ER_NO_REFERENCED_ROW_2

from app.auth import login_admin, login_required, logout_admin
from app.models import student as student_model
from app.models.admin import get_admin_by_username, verify_admin_password

bp = Blueprint("api", __name__)


@bp.route("/health")
def health():
    return jsonify({"status": "ok"}), 200


@bp.route("/api/login", methods=["POST"])
def api_login():
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""

    if not username or not password:
        return jsonify({"error": "username and password are required"}), 400

    admin = get_admin_by_username(username)
    if not admin or not verify_admin_password(admin, password):
        return jsonify({"error": "invalid credentials"}), 401

    login_admin(admin["admin_id"], admin["username"])
    return jsonify({"message": "login successful", "username": admin["username"]}), 200


@bp.route("/api/logout", methods=["POST"])
@login_required
def api_logout():
    logout_admin()
    return jsonify({"message": "logged out"}), 200


@bp.route("/api/students", methods=["GET"])
@login_required
def api_list_students():
    return jsonify(_serialize_all(student_model.get_all_students())), 200


@bp.route("/api/students", methods=["POST"])
@login_required
def api_create_student():
    data = request.get_json(silent=True) or {}
    payload, error = _validate_student_payload(data)
    if error:
        return jsonify({"error": error}), 400

    try:
        new_id = student_model.create_student(**payload)
    except IntegrityError as e:
        return _integrity_error_response(e)

    return jsonify(_serialize(student_model.get_student_by_id(new_id))), 201


@bp.route("/api/students/search", methods=["GET"])
@login_required
def api_search_students():
    # Registered before the /<int:student_id> routes' catch would apply --
    # Flask matches this literal path ahead of the int converter regardless
    # of declaration order, but keeping it visually grouped with the other
    # /students routes avoids any confusion about precedence.
    query = request.args.get("q", "").strip()
    if not query:
        return jsonify({"error": "query parameter 'q' is required"}), 400
    return jsonify(_serialize_all(student_model.search_students(query))), 200


@bp.route("/api/students/<int:student_id>", methods=["GET"])
@login_required
def api_get_student(student_id):
    s = student_model.get_student_by_id(student_id)
    if not s:
        return jsonify({"error": "student not found"}), 404
    return jsonify(_serialize(s)), 200


@bp.route("/api/students/<int:student_id>", methods=["PUT"])
@login_required
def api_update_student(student_id):
    if not student_model.get_student_by_id(student_id):
        return jsonify({"error": "student not found"}), 404

    data = request.get_json(silent=True) or {}
    payload, error = _validate_student_payload(data)
    if error:
        return jsonify({"error": error}), 400

    try:
        student_model.update_student(student_id, **payload)
    except IntegrityError as e:
        return _integrity_error_response(e)

    return jsonify(_serialize(student_model.get_student_by_id(student_id))), 200


@bp.route("/api/students/<int:student_id>", methods=["DELETE"])
@login_required
def api_delete_student(student_id):
    deleted = student_model.delete_student(student_id)
    if not deleted:
        return jsonify({"error": "student not found"}), 404
    return jsonify({"message": "student deleted"}), 200


def _validate_student_payload(data):
    """Validate + coerce a create/update request body.

    Returns (payload_dict, None) on success or (None, error_message) on
    failure, so create and update share one validation path instead of two.
    """
    full_name = (data.get("full_name") or "").strip()
    email = (data.get("email") or "").strip()
    phone = (data.get("phone") or "").strip() or None
    dept_id = data.get("dept_id")
    year = data.get("year")
    cgpa = data.get("cgpa")

    if not full_name or not email or dept_id is None or year is None:
        return None, "full_name, email, dept_id, and year are required"

    try:
        dept_id = int(dept_id)
        year = int(year)
        cgpa = float(cgpa) if cgpa is not None else None
    except (TypeError, ValueError):
        return None, "dept_id, year, and cgpa must be numeric"

    return {
        "full_name": full_name,
        "email": email,
        "phone": phone,
        "dept_id": dept_id,
        "year": year,
        "cgpa": cgpa,
    }, None


def _integrity_error_response(e):
    if e.errno == ER_DUP_ENTRY:
        return jsonify({"error": "a student with that email already exists"}), 409
    if e.errno == ER_NO_REFERENCED_ROW_2:
        return jsonify({"error": "dept_id does not reference an existing department"}), 400
    return jsonify({"error": "database integrity error"}), 400


def _serialize(s):
    """Convert non-JSON-native DB types (Decimal, datetime) to plain values."""
    return {
        "student_id": s["student_id"],
        "full_name": s["full_name"],
        "email": s["email"],
        "phone": s["phone"],
        "dept_id": s["dept_id"],
        "dept_name": s["dept_name"],
        "year": s["year"],
        "cgpa": float(s["cgpa"]) if s["cgpa"] is not None else None,
        "created_at": s["created_at"].isoformat() if s["created_at"] else None,
    }


def _serialize_all(students):
    return [_serialize(s) for s in students]