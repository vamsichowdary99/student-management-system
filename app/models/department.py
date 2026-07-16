"""Department lookups.

Departments are reference data seeded directly via seed.sql rather than
managed through the UI -- the plan doesn't call for department CRUD, and
keeping them read-only here avoids building admin screens nobody asked for.
"""
from app.db import get_connection


def get_all_departments():
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT dept_id, dept_name FROM departments ORDER BY dept_name")
        return cursor.fetchall()
    finally:
        conn.close()


def get_department_by_id(dept_id):
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT dept_id, dept_name FROM departments WHERE dept_id = %s",
            (dept_id,),
        )
        return cursor.fetchone()
    finally:
        conn.close()