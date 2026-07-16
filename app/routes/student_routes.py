"""Web routes for the admin UI: list/search, view, add, edit, delete students.

Create and edit share _save_student() so validation and the
duplicate-email / bad-department error handling live in exactly one place
instead of being duplicated across two view functions.
"""
from flask import Blueprint, flash, redirect, render_template, request, url_for
from mysql.connector import IntegrityError
from mysql.connector.errorcode import ER_DUP_ENTRY, ER_NO_REFERENCED_ROW_2

from app.auth import login_required
from app.models import department, student

bp = Blueprint("students", __name__)


@bp.route("/")
def index():
    return redirect(url_for("students.list_students"))


@bp.route("/students")
@login_required
def list_students():
    query = request.args.get("q", "").strip()
    students = student.search_students(query) if query else student.get_all_students()
    return render_template("students_list.html", students=students, query=query)


@bp.route("/students/<int:student_id>")
@login_required
def view_student(student_id):
    s = student.get_student_by_id(student_id)
    if not s:
        flash("Student not found", "error")
        return redirect(url_for("students.list_students"))
    return render_template("student_detail.html", student=s)


@bp.route("/students/new", methods=["GET", "POST"])
@login_required
def new_student():
    departments = department.get_all_departments()

    if request.method == "POST":
        error = _save_student(None, request.form)
        if error:
            flash(error, "error")
            return render_template(
                "student_form.html", departments=departments, student=request.form, mode="new"
            )
        flash("Student added", "success")
        return redirect(url_for("students.list_students"))

    return render_template("student_form.html", departments=departments, student=None, mode="new")


@bp.route("/students/<int:student_id>/edit", methods=["GET", "POST"])
@login_required
def edit_student(student_id):
    existing = student.get_student_by_id(student_id)
    if not existing:
        flash("Student not found", "error")
        return redirect(url_for("students.list_students"))

    departments = department.get_all_departments()

    if request.method == "POST":
        error = _save_student(student_id, request.form)
        if error:
            flash(error, "error")
            return render_template(
                "student_form.html",
                departments=departments,
                student=request.form,
                mode="edit",
                student_id=student_id,
            )
        flash("Student updated", "success")
        return redirect(url_for("students.view_student", student_id=student_id))

    return render_template(
        "student_form.html", departments=departments, student=existing, mode="edit", student_id=student_id
    )


@bp.route("/students/<int:student_id>/delete", methods=["POST"])
@login_required
def delete_student(student_id):
    student.delete_student(student_id)
    flash("Student deleted", "success")
    return redirect(url_for("students.list_students"))


def _save_student(student_id, form):
    """Shared create/update form handling. Returns an error message, or None on success."""
    full_name = form.get("full_name", "").strip()
    email = form.get("email", "").strip()
    phone = form.get("phone", "").strip() or None
    dept_id = form.get("dept_id", "")
    year = form.get("year", "")
    cgpa = form.get("cgpa", "").strip() or None

    if not full_name or not email or not dept_id or not year:
        return "Full name, email, department, and year are required."

    try:
        dept_id = int(dept_id)
        year = int(year)
        cgpa = float(cgpa) if cgpa else None
    except ValueError:
        return "Department, year, and CGPA must be numeric."

    try:
        if student_id is None:
            student.create_student(full_name, email, phone, dept_id, year, cgpa)
        else:
            student.update_student(student_id, full_name, email, phone, dept_id, year, cgpa)
    except IntegrityError as e:
        if e.errno == ER_DUP_ENTRY:
            return "A student with that email already exists."
        if e.errno == ER_NO_REFERENCED_ROW_2:
            return "Selected department does not exist."
        return "Could not save student."

    return None