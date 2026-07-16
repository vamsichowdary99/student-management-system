"""Centralized configuration, read from environment variables (see .env.example).

Keeping every setting in one class -- instead of scattering os.environ.get()
calls across the codebase -- means there is exactly one place to check when
something is misconfigured, and it makes the required environment obvious.
"""
import os

from dotenv import load_dotenv

# Load .env into the process environment for local/dev runs. In Docker,
# real environment variables set via docker-compose.yml are already present
# and take precedence over anything load_dotenv() would set.
load_dotenv()


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-me")

    DB_HOST = os.environ.get("DB_HOST", "localhost")
    DB_PORT = int(os.environ.get("DB_PORT", 3306))
    DB_NAME = os.environ.get("DB_NAME", "student_mgmt")
    DB_USER = os.environ.get("DB_USER", "app_user")
    DB_PASSWORD = os.environ.get("DB_PASSWORD", "app_password")