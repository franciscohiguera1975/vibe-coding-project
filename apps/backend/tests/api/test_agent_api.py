from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def _admin_headers() -> dict[str, str]:
    response = client.post(
        "/api/auth/login",
        json={"email": "admin@vibe-coding-platform.dev", "password": "AdminPass123!"},
    )
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def test_agent_run_endpoint(admin_user):
    headers = _admin_headers()
    created = client.post(
        "/api/practices",
        json={
            "title": "Practica del agente API",
            "type": "software",
            "instructions": "Resuelva Z",
            "content": {},
        },
        headers=headers,
    ).json()
    client.post(f"/api/practices/{created['id']}/publish", headers=headers)

    response = client.post(
        "/api/agent/run",
        json={"practice_slug": created["slug"], "user_message": "ayuda por favor"},
        headers=headers,
    )
    assert response.status_code == 200
    body = response.json()
    assert body["response"]
    assert body["iterations_used"] > 0
    assert body["session_id"]


def test_agent_run_requires_authentication():
    response = client.post("/api/agent/run", json={"practice_slug": "x", "user_message": "hola"})
    assert response.status_code == 403
