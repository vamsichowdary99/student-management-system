"""Student CRUD + search -- the core of the app.

Every query below uses %s placeholders, so user-supplied values are always
sent to MySQL as bound parameters and never string-concatenated into the SQL
text. That parameter binding is what makes raw SQL safe from SQL injection
here, instead of relying on an ORM to do it for us.
"""
from mysql.connector import IntegrityError

from app.db import get_connection

# Joined with departments so callers get a human-readable dept_name for
# free, instead of every caller having to look up the department separately.
_SELECT_BASE = """
    SELECT s.student_id, s.full_name, s.email, s.phone, s.dept_id,
           d.dept_name, s.year, s.cgpa, s.created_at
    FROM students s
    JOIN departments d ON s.dept_id = d.dept_id
"""


def get_all_students():
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(_SELECT_BASE + " ORDER BY s.full_name")
        return cursor.fetchall()
    finally:
        conn.close()


def get_student_by_id(student_id):
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(_SELECT_BASE + " WHERE s.student_id = %s", (student_id,))
        return cursor.fetchone()
    finally:
        conn.close()


def search_students(query):
    """Search by full name or email using a LIKE match.

    idx_students_full_name (schema.sql) keeps a name-prefix search fast. The
    email side uses a leading wildcard and can't use an index, but the table
    is small enough that this beginner-friendly project doesn't need
    MySQL's FULLTEXT search for that tradeoff to matter.
    """
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        like_pattern = f"%{query}%"
        cursor.execute(
            _SELECT_BASE + " WHERE s.full_name LIKE %s OR s.email LIKE %s ORDER BY s.full_name",
            (like_pattern, like_pattern),
        )
        return cursor.fetchall()
    finally:
        conn.close()


def create_student(full_name, email, phone, dept_id, year, cgpa):
    """Insert a student. Raises IntegrityError on a duplicate email or an
    unknown dept_id -- callers translate that into a 400/409 HTTP response."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO students (full_name, email, phone, dept_id, year, cgpa)
               VALUES (%s, %s, %s, %s, %s, %s)""",
            (full_name, email, phone, dept_id, year, cgpa),
        )
        conn.commit()
        return cursor.lastrowid
    except IntegrityError:
        conn.rollback()
        raise
    finally:
        conn.close()


def update_student(student_id, full_name, email, phone, dept_id, year, cgpa):
    """Update a student. Returns False if no row matched student_id."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """UPDATE students
               SET full_name = %s, email = %s, phone = %s, dept_id = %s, year = %s, cgpa = %s
               WHERE student_id = %s""",
            (full_name, email, phone, dept_id, year, cgpa, student_id),
        )
        conn.commit()
        return cursor.rowcount > 0
    except IntegrityError:
        conn.rollback()
        raise
    finally:
        conn.close()


def delete_student(student_id):
    """Delete a student. Returns False if no row matched student_id."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM students WHERE student_id = %s", (student_id,))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()