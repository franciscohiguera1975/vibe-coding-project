from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def _login(email: str, password: str) -> str:
    response = client.post("/api/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200
    return response.json()["access_token"]


def _admin_headers() -> dict[str, str]:
    token = _login("admin@vibe-coding-platform.dev", "AdminPass123!")
    return {"Authorization": f"Bearer {token}"}


def test_list_users_requires_permission(admin_user, random_email):
    headers = _admin_headers()
    client.post(
        "/api/users",
        json={"email": random_email, "full_name": "Nuevo", "password": "Password123!"},
        headers=headers,
    )

    response = client.get("/api/users", headers=headers)
    assert response.status_code == 200
    assert response.json()["total"] >= 2

    anon_response = client.get("/api/users")
    assert anon_response.status_code == 403


def test_create_and_list_categories(admin_user):
    headers = _admin_headers()
    created = client.post(
        "/api/practice-categories", json={"name": "Categoría de prueba"}, headers=headers
    )
    assert created.status_code == 201
    assert created.json()["slug"] == "categoria-de-prueba"

    listing = client.get("/api/practice-categories")
    assert listing.status_code == 200
    assert any(c["slug"] == "categoria-de-prueba" for c in listing.json())


def test_list_permissions(admin_user):
    headers = _admin_headers()
    response = client.get("/api/permissions", headers=headers)
    assert response.status_code == 200
    codes = {p["code"] for p in response.json()}
    assert "practice:create" in codes


def test_update_configuration(admin_user):
    headers = _admin_headers()
    response = client.put(
        "/api/configurations/platform.name",
        json={"value": {"value": "Mi Plataforma"}, "description": "Nombre"},
        headers=headers,
    )
    assert response.status_code == 200
    assert response.json()["value"]["value"] == "Mi Plataforma"

    listing = client.get("/api/configurations", headers=headers)
    assert any(c["key"] == "platform.name" for c in listing.json())


def test_audit_log_records_sensitive_actions(admin_user, random_email):
    headers = _admin_headers()
    client.post(
        "/api/users",
        json={"email": random_email, "full_name": "Auditado", "password": "Password123!"},
        headers=headers,
    )

    response = client.get("/api/audit-logs", headers=headers)
    assert response.status_code == 200
    actions = [a["action"] for a in response.json()["items"]]
    assert "user.create" in actions
