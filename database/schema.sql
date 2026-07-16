-- schema.sql
-- Defines the normalized schema for the Student Management System.
-- Loaded automatically by MySQL's /docker-entrypoint-initdb.d on first container start.
--
-- Design notes (for interview talking points):
--   * `departments` is split out into its own table (rather than a free-text column on
--     `students`) to demonstrate normalization: department names are stored once, and
--     `students.dept_id` references them by foreign key. This avoids duplication/typos
--     and lets us rename a department in one place.
--   * `email` is UNIQUE because it is the natural business key for a student.
--   * Indexes are added on the columns we actually filter/search/join by: `full_name`
--     (search), `dept_id` (FK join), and the implicit unique index on `email`.
--   * `admins.password_hash` never stores a plaintext password — see seed.sql, which
--     inserts a pre-computed werkzeug hash rather than raw text.

CREATE TABLE IF NOT EXISTS departments (
    dept_id     INT AUTO_INCREMENT PRIMARY KEY,
    dept_name   VARCHAR(100) NOT NULL,
    UNIQUE KEY uq_departments_dept_name (dept_name)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS students (
    student_id   INT AUTO_INCREMENT PRIMARY KEY,
    full_name    VARCHAR(150) NOT NULL,
    email        VARCHAR(150) NOT NULL,
    phone        VARCHAR(20),
    dept_id      INT NOT NULL,
    year         INT NOT NULL,
    cgpa         DECIMAL(3,2),
    created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_students_email (email),
    KEY idx_students_full_name (full_name),
    KEY idx_students_dept_id (dept_id),
    CONSTRAINT fk_students_dept
        FOREIGN KEY (dept_id) REFERENCES departments(dept_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS admins (
    admin_id       INT AUTO_INCREMENT PRIMARY KEY,
    username       VARCHAR(50) NOT NULL,
    password_hash  VARCHAR(255) NOT NULL,
    UNIQUE KEY uq_admins_username (username)
) ENGINE=InnoDB;