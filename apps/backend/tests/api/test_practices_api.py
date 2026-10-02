from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def _login(email: str, password: str) -> str:
    response = client.post("/api/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200
    return response.json()["access_token"]


def test_public_catalog_only_lists_published(admin_user):
    token = _login("admin@vibe-coding-platform.dev", "AdminPass123!")
    headers = {"Authorization": f"Bearer {token}"}

    created = client.post(
        "/api/practices",
        json={
            "title": "Conteo de circulos",
            "type": "image",
            "instructions": "x",
            "content": {"a": 1},
        },
        headers=headers,
    )
    assert created.status_code == 201
    practice_id = created.json()["id"]

    public_list = client.get("/api/practices")
    assert public_list.status_code == 200
    assert public_list.json()["total"] == 0

    publish = client.post(f"/api/practices/{practice_id}/publish", headers=headers)
    assert publish.status_code == 200
    assert publish.json()["status"] == "published"

    public_list_after = client.get("/api/practices")
    assert public_list_after.json()["total"] == 1

    public_detail = client.get(f"/api/practices/{created.json()['slug']}")
    assert public_detail.status_code == 200


def test_create_practice_requires_permission():
    response = client.post(
        "/api/practices",
        json={"title": "Sin permiso", "type": "software", "instructions": "x", "content": {}},
    )
    assert response.status_code == 403


def test_full_flow_via_api(admin_user, student_role, random_email):
    admin_token = _login("admin@vibe-coding-platform.dev", "AdminPass123!")
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    created = client.post(
        "/api/practices",
        json={
            "title": "MRU API",
            "type": "software",
            "instructions": "Prediga y calcule",
            "content": {"model": "distance = speed * time"},
            "evaluation": {
                "strategy": "numeric_match",
                "checks": [{"field": "distance_km", "expected": 60, "tolerance": 0.01}],
            },
        },
        headers=admin_headers,
    ).json()
    client.post(f"/api/practices/{created['id']}/publish", headers=admin_headers)

    student_created = client.post(
        "/api/users",
        json={"email": random_email, "full_name": "Estudiante API", "password": "Password123!"},
        headers=admin_headers,
    ).json()
    client.post(
        f"/api/users/{student_created['id']}/roles",
        json={"role_name": "STUDENT"},
        headers=admin_headers,
    )
    student_token = _login(random_email, "Password123!")
    student_headers = {"Authorization": f"Bearer {student_token}"}

    start = client.post(f"/api/practices/{created['slug']}/start", headers=student_headers)
    assert start.status_code == 200
    attempt_id = start.json()["id"]

    submit = client.post(
        "/api/practices/attempts/submit",
        json={"attempt_id": attempt_id, "payload": {"distance_km": 60}},
        headers=student_headers,
    )
    assert submit.status_code == 200
    submission_id = submit.json()["id"]

    evaluate = client.post(
        f"/api/practices/submissions/{submission_id}/evaluate", headers=student_headers
    )
    assert evaluate.status_code == 200
    assert evaluate.json()["passed"] is True
