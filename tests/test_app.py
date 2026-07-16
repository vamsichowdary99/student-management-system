"""Smoke tests: the app boots and its most basic routes behave correctly.

These deliberately avoid touching MySQL -- CI has no database service, and
these tests exist to catch a broken app factory, routing, or template, not
to re-verify SQL logic (that's what the Postman collection against a real
running stack is for; see postman_collection.json).
"""
import pytest

from app import create_app


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as test_client:
        yield test_client


def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


def test_login_page_renders(client):
    response = client.get("/login")
    assert response.status_code == 200
    assert b'name="username"' in response.data
    assert b'name="password"' in response.data


def test_students_page_requires_login(client):
    response = client.get("/students")
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_api_students_requires_login(client):
    response = client.get("/api/students")
    assert response.status_code == 401
    assert response.get_json() == {"error": "authentication required"}