from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_login_returns_tokens(admin_user):
    response = client.post(
        "/api/auth/login",
        json={"email": "admin@vibe-coding-platform.dev", "password": "AdminPass123!"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["user"]["email"] == "admin@vibe-coding-platform.dev"
    assert "ADMIN" in body["user"]["roles"]
    assert body["access_token"]


def test_login_rejects_wrong_password(admin_user):
    response = client.post(
        "/api/auth/login", json={"email": "admin@vibe-coding-platform.dev", "password": "wrong"}
    )
    assert response.status_code == 401


def test_me_requires_bearer_token():
    response = client.get("/api/auth/me")
    assert response.status_code == 403  # HTTPBearer sin credenciales


def test_me_returns_current_user(admin_user):
    login = client.post(
        "/api/auth/login",
        json={"email": "admin@vibe-coding-platform.dev", "password": "AdminPass123!"},
    )
    access_token = login.json()["access_token"]

    response = client.get("/api/auth/me", headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200
    assert response.json()["email"] == "admin@vibe-coding-platform.dev"


def test_create_user_requires_admin_permission(admin_user, random_email):
    login = client.post(
        "/api/auth/login",
        json={"email": "admin@vibe-coding-platform.dev", "password": "AdminPass123!"},
    )
    access_token = login.json()["access_token"]

    response = client.post(
        "/api/users",
        json={"email": random_email, "full_name": "Nuevo", "password": "Password123!"},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 201
    assert response.json()["email"] == random_email


def test_create_user_rejected_without_token(random_email):
    response = client.post(
        "/api/users",
        json={"email": random_email, "full_name": "Nuevo", "password": "Password123!"},
    )
    assert response.status_code == 403


def test_password_reset_request_returns_204_for_unknown_email():
    response = client.post(
        "/api/auth/password-reset/request", json={"email": "nobody@vibe-coding-platform.dev"}
    )
    assert response.status_code == 204


def test_password_reset_full_flow(admin_user):
    import app.interfaces.http.dependencies.email as email_deps

    class _CapturingEmailSender:
        def __init__(self) -> None:
            self.reset_url: str | None = None

        def send_password_reset_email(self, *, to_email, full_name, reset_url) -> None:
            self.reset_url = reset_url

    capturing_sender = _CapturingEmailSender()
    email_deps.get_email_sender.cache_clear()
    app.dependency_overrides[email_deps.get_email_sender] = lambda: capturing_sender
    try:
        request_response = client.post(
            "/api/auth/password-reset/request",
            json={"email": "admin@vibe-coding-platform.dev"},
        )
        assert request_response.status_code == 204
        assert capturing_sender.reset_url is not None
        token = capturing_sender.reset_url.split("token=", 1)[1]

        confirm_response = client.post(
            "/api/auth/password-reset/confirm",
            json={"token": token, "new_password": "NuevaClave123!"},
        )
        assert confirm_response.status_code == 204

        login_response = client.post(
            "/api/auth/login",
            json={"email": "admin@vibe-coding-platform.dev", "password": "NuevaClave123!"},
        )
        assert login_response.status_code == 200
    finally:
        app.dependency_overrides.pop(email_deps.get_email_sender, None)


def test_password_reset_confirm_rejects_invalid_token():
    response = client.post(
        "/api/auth/password-reset/confirm",
        json={"token": "token-invalido", "new_password": "NuevaClave123!"},
    )
    assert response.status_code == 400


def test_assign_role_and_list_roles(admin_user, student_role, random_email):
    login = client.post(
        "/api/auth/login",
        json={"email": "admin@vibe-coding-platform.dev", "password": "AdminPass123!"},
    )
    access_token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}

    created = client.post(
        "/api/users",
        json={"email": random_email, "full_name": "Nuevo", "password": "Password123!"},
        headers=headers,
    ).json()

    response = client.post(
        f"/api/users/{created['id']}/roles", json={"role_name": "STUDENT"}, headers=headers
    )
    assert response.status_code == 200
    assert "STUDENT" in response.json()["roles"]

    roles_response = client.get("/api/roles", headers=headers)
    assert roles_response.status_code == 200
    assert any(r["name"] == "STUDENT" for r in roles_response.json())
