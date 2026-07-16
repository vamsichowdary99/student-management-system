# Plan: Cloud-Native Student Management System (Placement Project)

## Context

Build a **Student Management System** as a final-year campus-placement portfolio project targeting
**DevOps / Cloud / Software Engineer** roles. The goal is a *realistic, beginner-friendly* app that
demonstrably exercises **Python (Flask), MySQL, Docker, Git, AWS EC2, and GitHub Actions CI/CD** —
something a student can build in 3–4 weeks and confidently explain in interviews.

**Out of scope (do NOT use):** Kubernetes, Terraform, Jenkins, Redis, RabbitMQ, Kafka, microservices,
or any advanced cloud architecture. Keep it clear, modular, and well-commented.

**Confirmed decisions:**
1. **Fresh dedicated git repo** in the project folder, new GitHub remote under `tanjirokamodo`.
   (The folder currently sits inside a home-directory repo with an unrelated project + wrong remote —
   run a fresh `git init` in the project folder to escape it.)
2. **Flask + Jinja2 server-rendered web UI** *plus* JSON REST APIs (for Postman testing).
3. **Full CI/CD**: build → test → auto-deploy to EC2 over SSH (secrets configured once EC2 exists).

Deliver **incrementally**, explaining each file as it is created so the project doubles as a learning exercise.

---

## Architecture at a glance

- **Backend:** Flask app-factory pattern, **raw parameterized SQL** via `mysql-connector-python`
  (raw SQL over an ORM to *demonstrate SQL skills* and safe parameterization for interviews).
- **Auth:** Flask server-side sessions; admin credentials in an `admins` table with
  `werkzeug.security` password hashing. A `@login_required` decorator guards protected routes/APIs.
- **DB (normalized, 3 tables):**
  - `departments(dept_id PK, dept_name UNIQUE)`
  - `students(student_id PK, full_name, email UNIQUE, phone, dept_id FK→departments, year, cgpa, created_at)`
  - `admins(admin_id PK, username UNIQUE, password_hash)`
  - Indexes: unique on `email`, index on `full_name` (search), FK index on `dept_id`.
  - The `departments` FK is deliberate — it enables a **normalization + foreign keys** interview story.
- **Containers:** `web` (Flask/Gunicorn) + `db` (mysql:8.0) via Docker Compose; `schema.sql` + `seed.sql`
  auto-loaded through MySQL's `/docker-entrypoint-initdb.d`. One command: `docker compose up`.
- **CI/CD:** GitHub Actions on push to `main` → lint/test → build image → SSH deploy to EC2.

---

## Proposed folder structure (all new files)

```
cloud cicd project/
├── app/
│   ├── __init__.py          # Flask app factory, session config, blueprint registration
│   ├── config.py            # Reads DB creds / SECRET_KEY from environment
│   ├── db.py                # get_connection() helper (mysql-connector)
│   ├── auth.py              # login_required decorator, session helpers
│   ├── models/
│   │   ├── student.py       # CRUD + search SQL for students
│   │   ├── department.py    # department lookups
│   │   └── admin.py         # admin fetch + password verify
│   ├── routes/
│   │   ├── auth_routes.py    # /login, /logout (web forms)
│   │   ├── student_routes.py # web pages: list/add/edit/view/delete/search
│   │   └── api_routes.py     # /api/* JSON REST endpoints
│   ├── templates/           # base, login, students_list, student_form, student_detail
│   └── static/css/style.css # simple clean styling
├── database/
│   ├── schema.sql            # tables, constraints, indexes
│   └── seed.sql              # sample departments/students + default admin (admin/admin123)
├── tests/
│   └── test_app.py           # pytest: app boots, /login renders, health endpoint
├── run.py                    # local entrypoint (flask app factory)
├── requirements.txt          # Flask, mysql-connector-python, gunicorn, python-dotenv, pytest, flake8
├── Dockerfile                # python:3.11-slim → gunicorn
├── docker-compose.yml        # web + db services, volume, healthcheck, depends_on
├── .env.example              # documents all env vars (never commit real .env)
├── .gitignore                # __pycache__, .env, venv, etc.
├── .dockerignore
├── .github/workflows/ci-cd.yml
├── postman_collection.json   # importable API collection
└── README.md                 # full documentation
```

---

## Build sequence (incremental milestones)

Each milestone is independently verifiable and gets its own clean commit.

**M1 — Repo & scaffolding**
- Fresh `git init` in the project folder; add `.gitignore`, `.dockerignore`, `requirements.txt`, folder skeleton.
- Set `COMPOSE_PROJECT_NAME=student-mgmt` in `.env` to avoid Docker naming issues from the space in the folder name.
- *Verify:* `git status` clean-and-scoped; `git rev-parse --show-toplevel` points at the project folder.

**M2 — Database layer**
- Write `database/schema.sql` (normalized tables + FK + indexes) and `database/seed.sql`
  (departments, ~5 sample students, default admin with a pre-hashed password).
- *Verify:* schema loads without error in a throwaway MySQL container.

**M3 — Flask backend (config, db, models, auth)**
- `config.py`, `db.py`, `auth.py`, and the three `models/*.py` with parameterized CRUD/search SQL.
- App factory in `app/__init__.py`; `run.py` entrypoint.
- *Verify:* `python run.py` boots against a local/compose MySQL.

**M4 — REST APIs + web UI**
- `api_routes.py`: `POST /api/login`, `GET/POST /api/students`, `GET/PUT/DELETE /api/students/<id>`,
  `GET /api/students/search?q=`, `GET /health`. Proper HTTP codes (200/201/400/401/404) + JSON.
- `auth_routes.py` + `student_routes.py` + Jinja templates for the admin UI.
- *Verify:* Postman collection runs green; browse the UI to add/edit/delete/search a student.

**M5 — Dockerization**
- `Dockerfile` (gunicorn) + `docker-compose.yml` (web+db, healthcheck, initdb mount, volume).
- *Verify:* `docker compose up` from a clean state → app reachable at `http://localhost:5000`, data persists across restart.

**M6 — CI/CD pipeline**
- `.github/workflows/ci-cd.yml`: on push to `main` → set up Python → install → `flake8` + `pytest`
  → build image → deploy job using `appleboy/ssh-action` to `ssh → git pull → docker compose up -d --build`.
- Documents required secrets: `EC2_HOST`, `EC2_USER`, `EC2_SSH_KEY`.
- *Verify:* workflow YAML validates; CI (lint+test+build) passes on first push. Deploy job activates once EC2 secrets are set.

**M7 — Docs & AWS runbook**
- `README.md`: overview, features, tech stack, folder structure, local + Docker setup, **step-by-step
  AWS EC2 deployment** (launch instance, security group ports 22/5000, SSH, install Docker, clone, run),
  API reference table, screenshot placeholders, future improvements.
- `postman_collection.json` finalized.
- *Verify:* a fresh reader can follow README from zero to running app.

---

## Key implementation notes

- **Security-for-learning:** all SQL uses parameter binding (`%s`) — call this out in comments/README
  as SQL-injection prevention. Passwords hashed with `werkzeug.security`. `SECRET_KEY` from env.
- **Default admin:** `admin` / `admin123`, seeded via pre-computed hash in `seed.sql`; README tells the
  user to change it. Flagged as a demo-only credential.
- **Config via env only:** no secrets committed; `.env.example` documents every variable; real `.env` gitignored.
- **Gunicorn** in the container (not Flask dev server) — a small but real "production-ready" talking point.

## Verification (end-to-end)

1. `docker compose up --build` from empty state → `http://localhost:5000` loads login page.
2. Log in as admin → add / edit / search / delete a student through the web UI.
3. Import `postman_collection.json` → run login + full CRUD + search; confirm status codes & JSON.
4. `pytest` and `flake8` pass locally (same as CI).
5. Restart compose → seeded + added data persists (volume works).
6. (When AWS ready) push to `main` → GitHub Actions builds, tests, and deploys; app reachable at EC2 public IP:5000.

## Open follow-ups (handled during build, not blockers)
- Creating the GitHub repo under `tanjirokamodo` and wiring the remote (`gh` or GitHub MCP).
- Actual AWS EC2 provisioning is a manual step; README provides the exact runbook.
