# Cloud-Native Student Management System

A small, realistic **Student Management System** built to demonstrate Python/Flask,
MySQL, Docker, Git, and CI/CD fundamentals for DevOps / Cloud / Software Engineer
placement interviews. It's deliberately beginner-friendly: no Kubernetes, Terraform,
Jenkins, Redis, or microservices -- just a clean, well-commented monolith that's
easy to explain end-to-end.

## Features

- Admin authentication (Flask server-side sessions, `werkzeug` password hashing)
- Full CRUD on students, plus name/email search, through **both**:
  - a server-rendered Jinja2 web UI, and
  - a JSON REST API (for Postman / programmatic clients)
- Normalized MySQL schema (`departments` / `students` / `admins`) with foreign keys
  and indexes
- Every query is **raw parameterized SQL** (`mysql-connector-python`, no ORM) --
  demonstrates SQL skill and safe parameter binding against SQL injection
- Dockerized with Docker Compose (`web` + `db`, healthchecks, a persistent volume)
- CI/CD via GitHub Actions: lint -> test -> build -> deploy to EC2 over SSH

## Tech Stack

| Layer          | Choice                                              |
|----------------|------------------------------------------------------|
| Backend        | Python 3.11, Flask (app-factory pattern), Gunicorn   |
| Database       | MySQL 8.0, raw SQL via `mysql-connector-python`      |
| Auth           | Flask sessions + `werkzeug.security` password hashing |
| Containers     | Docker, Docker Compose                                |
| CI/CD          | GitHub Actions                                        |
| API testing    | Postman / Newman                                      |
| Hosting        | AWS EC2                                               |

## Folder Structure

```
cloud cicd project/
├── app/
│   ├── __init__.py          # Flask app factory + blueprint registration
│   ├── config.py            # Env-based configuration
│   ├── db.py                # mysql-connector connection helper
│   ├── auth.py               # login_required decorator + session helpers
│   ├── models/               # student.py, department.py, admin.py -- raw SQL
│   ├── routes/                # auth_routes.py, student_routes.py, api_routes.py
│   ├── templates/             # Jinja2 templates for the admin UI
│   └── static/css/style.css
├── database/
│   ├── schema.sql             # tables, FK constraints, indexes
│   └── seed.sql                # sample departments/students + default admin
├── tests/test_app.py          # pytest smoke tests (no DB required)
├── run.py                      # local dev entrypoint
├── requirements.txt
├── Dockerfile                   # python:3.11-slim -> gunicorn
├── docker-compose.yml            # web + db services
├── .env.example                   # documents every required env var
├── .github/workflows/ci-cd.yml     # lint -> test -> build -> deploy
└── postman_collection.json          # importable API test collection
```

## Local Setup (without Docker)

```bash
python -m venv .venv
source .venv/Scripts/activate      # Windows Git Bash; use .venv\Scripts\activate on cmd
pip install -r requirements.txt

cp .env.example .env
# edit .env: point DB_HOST/DB_PORT at any MySQL 8.0 instance you have running,
# and load database/schema.sql then database/seed.sql into it.

python run.py
# visit http://localhost:5000
```

## Docker Setup (recommended)

```bash
cp .env.example .env
docker compose up --build
# visit http://localhost:5000
```

`docker compose` reads `.env` automatically. `COMPOSE_PROJECT_NAME=student-mgmt` is
set there deliberately -- this folder's name contains spaces
("cloud cicd project"), which would otherwise produce a messy default Compose
project/network name.

To stop and remove containers (keeping data): `docker compose down`
To also wipe the database volume: `docker compose down -v`

## Default Admin Credentials

```
username: admin
password: admin123
```

This is seeded via a pre-computed password hash in `database/seed.sql` --
**demo credentials only**. Change them before any real deployment by generating a
new hash and updating the `admins` table:

```bash
python -c "from werkzeug.security import generate_password_hash as g; print(g('your-new-password'))"
# then, in MySQL:
# UPDATE admins SET password_hash = '<hash above>' WHERE username = 'admin';
```

## API Reference

All `/api/*` routes (except `/api/login` and `/health`) require an authenticated
session -- call `POST /api/login` first and reuse the session cookie.

| Method | Endpoint                     | Auth | Description                          |
|--------|-------------------------------|------|---------------------------------------|
| GET    | `/health`                     | No   | Health check                          |
| POST   | `/api/login`                  | No   | Log in, starts a session               |
| POST   | `/api/logout`                 | Yes  | Log out, clears the session             |
| GET    | `/api/students`               | Yes  | List all students                        |
| POST   | `/api/students`                | Yes  | Create a student                          |
| GET    | `/api/students/<id>`            | Yes  | Get one student                            |
| PUT    | `/api/students/<id>`             | Yes  | Update a student                            |
| DELETE | `/api/students/<id>`              | Yes  | Delete a student                              |
| GET    | `/api/students/search?q=<query>`   | Yes  | Search by name or email                        |

Status codes: `200` success, `201` created, `400` validation error, `401` not
authenticated, `404` not found, `409` duplicate email.

## Postman Collection

Import `postman_collection.json` into Postman (or run it headlessly):

```bash
npx newman run postman_collection.json
```

Run the whole collection top-to-bottom -- Postman's cookie jar keeps the session
alive across requests automatically. It covers the full auth + CRUD + search flow,
including the 400/404/409 error cases, and logs out at the very end.

## Testing & Linting

```bash
pytest       # DB-free smoke tests: app boots, health check, login page, auth guarding
flake8 app run.py tests
```

These are exactly what the CI pipeline runs on every push/PR.

## CI/CD Pipeline

`.github/workflows/ci-cd.yml` runs on every push/PR to `main`:

1. **lint-and-test** -- `flake8` + `pytest`
2. **build** -- `docker build` (proves the image actually builds)
3. **deploy** -- only on a push to `main`, SSHes into an EC2 instance, `git pull`s,
   and runs `docker compose up -d --build`. This step is automatically **skipped**
   (not failed) until the required secrets below are configured.

Required repository secrets (**Settings > Secrets and variables > Actions**):

| Secret        | Value                                              |
|----------------|------------------------------------------------------|
| `EC2_HOST`      | Public IP or DNS name of your EC2 instance             |
| `EC2_USER`       | SSH username (`ubuntu` for Ubuntu AMIs)                 |
| `EC2_SSH_KEY`     | Full contents of the private key (`.pem`) for that instance |

## AWS EC2 Deployment Runbook

1. **Launch an instance**: EC2 console -> Launch Instance -> Ubuntu 22.04 LTS,
   `t2.micro` (free tier eligible). Create/select a key pair and download the `.pem`.
2. **Security group**: allow inbound
   - port `22` (SSH) from your IP
   - port `5000` (the app) from your IP, or `0.0.0.0/0` to make it public
3. **Connect**:
   ```bash
   chmod 400 your-key.pem
   ssh -i your-key.pem ubuntu@<EC2_PUBLIC_IP>
   ```
4. **Install Docker + Compose + git** on the instance:
   ```bash
   sudo apt update
   sudo apt install -y docker.io docker-compose-plugin git
   sudo usermod -aG docker $USER
   # log out and back in for the group change to take effect
   ```
5. **Clone and configure**:
   ```bash
   git clone <your-repo-url> student-management-system
   cd student-management-system
   cp .env.example .env
   # edit .env: set a strong SECRET_KEY and DB passwords for production
   ```
6. **Run it**:
   ```bash
   docker compose up -d --build
   ```
   Visit `http://<EC2_PUBLIC_IP>:5000`.
7. **Wire up auto-deploy** (optional): add the three repo secrets from the table
   above. Every push to `main` will then SSH in, `git pull`, and
   `docker compose up -d --build` automatically.

## Screenshots

_(Add screenshots of the login page, student list, and add/edit form here once
the app is running.)_

## Future Improvements

- Pagination for large student lists
- Role-based access (multiple admin permission levels)
- A reverse proxy (nginx) in front of Gunicorn with HTTPS
- Automated MySQL backups
- Rate limiting on the login endpoint