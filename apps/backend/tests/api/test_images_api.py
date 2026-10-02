import io

from fastapi.testclient import TestClient
from PIL import Image, ImageDraw

from app.main import app

client = TestClient(app)


def _admin_headers() -> dict[str, str]:
    response = client.post(
        "/api/auth/login",
        json={"email": "admin@vibe-coding-platform.dev", "password": "AdminPass123!"},
    )
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def _circles_png(n: int) -> bytes:
    image = Image.new("RGB", (120, 120), color=(255, 255, 255))
    draw = ImageDraw.Draw(image)
    for i in range(n):
        x = 10 + (i % 3) * 35
        y = 10 + (i // 3) * 35
        draw.ellipse([x, y, x + 25, y + 25], fill=(200, 30, 30))
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def test_analyze_image_endpoint_returns_count_and_stores_file(admin_user):
    headers = _admin_headers()
    created = client.post(
        "/api/practices",
        json={
            "title": "Conteo API",
            "type": "image",
            "instructions": "Cuente circulos",
            "content": {
                "counting_rule": {
                    "counts": "un circulo con centro visible",
                    "excludes": ["sombras"],
                    "illegible_when": ["desenfoque"],
                }
            },
        },
        headers=headers,
    ).json()
    client.post(f"/api/practices/{created['id']}/publish", headers=headers)

    response = client.post(
        "/api/images/analyze",
        data={"practice_slug": created["slug"]},
        files={"file": ("circles.png", _circles_png(3), "image/png")},
        headers=headers,
    )
    assert response.status_code == 200
    body = response.json()
    assert body["count"] == 3
    assert body["key"]
    assert body["url"].endswith(f"/api/storage/{body['key']}")

    download = client.get(f"/api/storage/{body['key']}", headers=headers)
    assert download.status_code == 200
    assert download.content == _circles_png(3)


def test_analyze_image_endpoint_rejects_non_image(admin_user):
    headers = _admin_headers()
    created = client.post(
        "/api/practices",
        json={"title": "Conteo API 2", "type": "image", "instructions": "x", "content": {}},
        headers=headers,
    ).json()
    client.post(f"/api/practices/{created['id']}/publish", headers=headers)

    response = client.post(
        "/api/images/analyze",
        data={"practice_slug": created["slug"]},
        files={"file": ("fake.png", b"not-an-image", "image/png")},
        headers=headers,
    )
    assert response.status_code == 422


def test_analyze_image_requires_authentication():
    response = client.post(
        "/api/images/analyze",
        data={"practice_slug": "x"},
        files={"file": ("a.png", _circles_png(1), "image/png")},
    )
    assert response.status_code == 403
