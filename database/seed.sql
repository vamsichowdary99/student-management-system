-- seed.sql
-- Sample data loaded after schema.sql (files run in filename order in
-- /docker-entrypoint-initdb.d). Gives the app something to demo immediately
-- after `docker compose up` with no manual data entry.
--
-- The admin password below is NOT plaintext: it's a werkzeug (scrypt)
-- hash of "admin123", generated once with:
--   python -c "from werkzeug.security import generate_password_hash as g; print(g('admin123'))"
-- Login credentials for the demo: admin / admin123
-- DEMO CREDENTIAL ONLY — change this before any real deployment (see README).

INSERT INTO departments (dept_name) VALUES
    ('Computer Science'),
    ('Electronics & Communication'),
    ('Mechanical Engineering'),
    ('Civil Engineering'),
    ('Information Technology');

INSERT INTO students (full_name, email, phone, dept_id, year, cgpa) VALUES
    ('Aditi Sharma',   'aditi.sharma@example.com',   '9876543210', 1, 3, 8.75),
    ('Rohan Verma',    'rohan.verma@example.com',    '9876543211', 1, 4, 7.90),
    ('Priya Nair',     'priya.nair@example.com',     '9876543212', 2, 2, 9.10),
    ('Karan Mehta',    'karan.mehta@example.com',    '9876543213', 3, 3, 6.85),
    ('Sneha Reddy',    'sneha.reddy@example.com',    '9876543214', 5, 1, 8.20);

INSERT INTO admins (username, password_hash) VALUES
    ('admin', 'scrypt:32768:8:1$NlMGQwyRBA3RiOjP$fcc195a6e112e2045e66212ac233369636ab9c1d797b7807512670fbaf85661b2b30eef7773ff148f3a9a0f6b7628a292e03f2f821b13ab3dfc3ff7b250d87d7');