from fastapi.testclient import TestClient

from app.interfaces.http.dependencies.practice_use_cases import (
    get_generate_practice_narration_use_case,
)
from app.main import app

client = TestClient(app)


def _admin_headers() -> dict[str, str]:
    response = client.post(
        "/api/auth/login",
        json={"email": "admin@vibe-coding-platform.dev", "password": "AdminPass123!"},
    )
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def _create_published_practice(headers: dict[str, str]) -> dict:
    created = client.post(
        "/api/practices",
        json={
            "title": "Practica con narracion",
            "type": "software",
            "instructions": "Resuelva el problema de MRU",
            "objectives": ["Comprender distancia"],
            "content": {"model": "distance = speed * time"},
        },
        headers=headers,
    ).json()
    client.post(f"/api/practices/{created['id']}/publish", headers=headers)
    return created


def test_generate_narration_requires_permission(admin_user):
    headers = _admin_headers()
    practice = _create_published_practice(headers)

    response = client.post(f"/api/practices/{practice['slug']}/narration", params={"lang": "es"})
    assert response.status_code == 403


def test_narration_is_404_before_generation_and_200_after(admin_user):
    headers = _admin_headers()
    practice = _create_published_practice(headers)

    before = client.get(f"/api/practices/{practice['slug']}/narration", params={"lang": "es"})
    assert before.status_code == 404

    generated = client.post(
        f"/api/practices/{practice['slug']}/narration", params={"lang": "es"}, headers=headers
    )
    assert generated.status_code == 200
    body = generated.json()
    assert body["lang"] == "es"
    assert body["cached"] is False
    assert body["url"]

    after = client.get(f"/api/practices/{practice['slug']}/narration", params={"lang": "es"})
    assert after.status_code == 200
    assert after.json()["url"] == body["url"]

    regenerated = client.post(
        f"/api/practices/{practice['slug']}/narration", params={"lang": "es"}, headers=headers
    )
    assert regenerated.status_code == 200
    assert regenerated.json()["cached"] is True


def test_generate_all_returns_partial_results_when_one_language_fails(admin_user):
    headers = _admin_headers()
    practice = _create_published_practice(headers)

    class _FlakyUseCase:
        """Envoltorio que falla deliberadamente solo para `fr`, para probar que
        generate-all no aborta las demas narraciones ante un error puntual."""

        def __init__(self, real_use_case) -> None:
            self._real = real_use_case

        def execute(self, *, actor, slug, lang):
            if lang == "fr":
                raise RuntimeError("fallo simulado del proveedor de narracion")
            return self._real.execute(actor=actor, slug=slug, lang=lang)

    # Override via FastAPI's dependency_overrides: envolvemos la factory real.
    from app.application.use_cases.practices.generate_practice_narration import (
        GeneratePracticeNarrationUseCase,
    )
    from app.interfaces.http.dependencies.narration import get_narration_port
    from app.interfaces.http.dependencies.storage import get_storage_port
    from app.interfaces.http.dependencies.unit_of_work import get_uow_factory

    def _override():
        uow_factory = get_uow_factory()
        narration_port = get_narration_port()
        storage_port = get_storage_port()
        real = GeneratePracticeNarrationUseCase(uow_factory, narration_port, storage_port)
        return _FlakyUseCase(real)

    app.dependency_overrides[get_generate_practice_narration_use_case] = _override
    try:
        response = client.post(
            f"/api/practices/{practice['slug']}/narration/generate-all", headers=headers
        )
    finally:
        app.dependency_overrides.pop(get_generate_practice_narration_use_case, None)

    assert response.status_code == 200
    results = {item["lang"]: item for item in response.json()}
    assert set(results.keys()) == {"es", "en", "pt", "fr"}
    assert results["fr"]["status"] == "error"
    assert "fallo simulado" in results["fr"]["message"]
    for lang in ("es", "en", "pt"):
        assert results[lang]["status"] == "ok"
        assert results[lang]["url"]
