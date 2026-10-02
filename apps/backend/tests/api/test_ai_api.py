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


def test_generate_hint_endpoint(admin_user):
    headers = _admin_headers()
    created = client.post(
        "/api/practices",
        json={
            "title": "Practica con hint",
            "type": "software",
            "instructions": "Resuelva X",
            "content": {},
        },
        headers=headers,
    ).json()
    client.post(f"/api/practices/{created['id']}/publish", headers=headers)

    response = client.post(
        "/api/ai/hint",
        json={"practice_slug": created["slug"], "student_context": "ya intente dos veces"},
        headers=headers,
    )
    assert response.status_code == 200
    assert response.json()["hint"]


def test_generate_hint_requires_authentication():
    response = client.post("/api/ai/hint", json={"practice_slug": "x"})
    assert response.status_code == 403


def test_generate_feedback_endpoint(admin_user):
    headers = _admin_headers()
    created = client.post(
        "/api/practices",
        json={
            "title": "Practica con feedback",
            "type": "software",
            "instructions": "Resuelva Y",
            "content": {"notes": "informe manual"},
            "evaluation": {"strategy": "manual"},
        },
        headers=headers,
    ).json()
    client.post(f"/api/practices/{created['id']}/publish", headers=headers)

    start = client.post(f"/api/practices/{created['slug']}/start", headers=headers).json()
    submit = client.post(
        "/api/practices/attempts/submit",
        json={"attempt_id": start["id"], "payload": {}},
        headers=headers,
    ).json()

    response = client.post(
        "/api/ai/feedback", json={"submission_id": submit["id"]}, headers=headers
    )
    assert response.status_code == 200
    assert response.json()["feedback"]
