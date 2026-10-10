import io

from docx import Document
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def _docx_bytes(paragraphs: list[str]) -> bytes:
    document = Document()
    for paragraph in paragraphs:
        document.add_paragraph(paragraph)
    buffer = io.BytesIO()
    document.save(buffer)
    return buffer.getvalue()


def _admin_headers() -> dict[str, str]:
    response = client.post(
        "/api/auth/login",
        json={"email": "admin@vibe-coding-platform.dev", "password": "AdminPass123!"},
    )
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def test_validate_syllabus_requires_authentication():
    response = client.post("/api/rag/validate-syllabus", json={"text": "un silabo"})
    assert response.status_code == 403


def test_validate_syllabus_returns_five_checklist_items(admin_user):
    headers = _admin_headers()
    response = client.post(
        "/api/rag/validate-syllabus",
        json={"text": "Objetivos: X. Contenidos: unidad 1. Metodologia: Y."},
        headers=headers,
    )
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 5
    for item in body:
        assert "item" in item
        assert "cumple" in item
        assert "explicacion" in item
        assert "citas" in item


def test_validate_syllabus_upload_requires_authentication():
    response = client.post(
        "/api/rag/validate-syllabus/upload",
        files={
            "file": (
                "silabo.docx",
                _docx_bytes(["Objetivos: X.", "Contenidos: unidad 1.", "Metodologia: Y."]),
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
        },
    )
    assert response.status_code == 403


def test_validate_syllabus_upload_returns_five_checklist_items(admin_user):
    headers = _admin_headers()
    response = client.post(
        "/api/rag/validate-syllabus/upload",
        files={
            "file": (
                "silabo.docx",
                _docx_bytes(["Objetivos: X.", "Contenidos: unidad 1.", "Metodologia: Y."]),
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
        },
        headers=headers,
    )
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 5
    for item in body:
        assert "item" in item
        assert "cumple" in item
        assert "explicacion" in item
        assert "citas" in item


def test_validate_syllabus_upload_rejects_non_docx_file(admin_user):
    headers = _admin_headers()
    response = client.post(
        "/api/rag/validate-syllabus/upload",
        files={"file": ("silabo.txt", b"Objetivos: X. Contenidos: Y.", "text/plain")},
        headers=headers,
    )
    assert response.status_code == 422


def test_validate_syllabus_upload_rejects_corrupt_docx_file(admin_user):
    headers = _admin_headers()
    response = client.post(
        "/api/rag/validate-syllabus/upload",
        files={
            "file": (
                "silabo.docx",
                b"esto no es un archivo docx real, solo bytes arbitrarios",
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
        },
        headers=headers,
    )
    assert response.status_code == 422


def test_run_evaluation_requires_permission():
    # Sin Authorization: HTTPBearer(auto_error=True) rechaza con 403 (igual que
    # /api/ai/hint y /api/practices/{slug}/narration sin credenciales).
    response = client.post("/api/rag/evaluation/run")
    assert response.status_code == 403


def test_run_evaluation_and_get_latest(admin_user):
    headers = _admin_headers()

    not_found = client.get("/api/rag/evaluation")
    assert not_found.status_code == 404

    run_response = client.post("/api/rag/evaluation/run", headers=headers)
    assert run_response.status_code == 200
    run_body = run_response.json()
    assert run_body["summary"]["total"] == 15
    assert run_body["summary"]["baseline_citation_matches"] == 0
    assert len(run_body["results"]) == 15

    latest = client.get("/api/rag/evaluation")
    assert latest.status_code == 200
    assert latest.json()["id"] == run_body["id"]
