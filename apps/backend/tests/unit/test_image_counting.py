import io

from PIL import Image, ImageDraw, ImageFilter

from app.infrastructure.ai.image_counting import count_colored_regions
from app.infrastructure.ai.mock_adapter import MockAIAdapter


def _draw_circles_image(n: int, size: tuple[int, int] = (200, 200)) -> Image.Image:
    image = Image.new("RGB", size, color=(255, 255, 255))
    draw = ImageDraw.Draw(image)
    colors = [(220, 30, 30), (30, 120, 220), (30, 180, 60), (230, 180, 20)]
    for i in range(n):
        x = 20 + (i % 4) * 45
        y = 20 + (i // 4) * 45
        draw.ellipse([x, y, x + 30, y + 30], fill=colors[i % len(colors)])
    return image


def _to_png_bytes(image: Image.Image) -> bytes:
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def _draw_circles(n: int, size: tuple[int, int] = (200, 200)) -> bytes:
    return _to_png_bytes(_draw_circles_image(n, size))


def test_count_colored_regions_matches_number_of_circles():
    image_bytes = _draw_circles(3)
    count, details = count_colored_regions(image_bytes)
    assert count == 3
    assert details["image_size"] == [200, 200]


def test_count_colored_regions_empty_scene_is_zero():
    blank = Image.new("RGB", (100, 100), color=(255, 255, 255))
    buffer = io.BytesIO()
    blank.save(buffer, format="PNG")
    count, details = count_colored_regions(buffer.getvalue())
    assert count == 0
    assert details["illegible"] is False


def test_count_colored_regions_blurry_image_is_illegible():
    # Regla de la guia: una imagen borrosa se declara ilegible (no se cuenta), a
    # diferencia de una escena vacia, que cuenta 0 sin marcarse como ilegible.
    sharp_image = _draw_circles_image(5)
    blurred = sharp_image.filter(ImageFilter.GaussianBlur(radius=3))
    buffer = io.BytesIO()
    blurred.save(buffer, format="PNG")
    count, details = count_colored_regions(buffer.getvalue())
    assert details["illegible"] is True
    assert count == 0


def test_mock_adapter_analyze_image_warns_illegible_on_blur_without_hiding_it_as_empty():
    sharp_image = _draw_circles_image(5)
    blurred = sharp_image.filter(ImageFilter.GaussianBlur(radius=3))
    buffer = io.BytesIO()
    blurred.save(buffer, format="PNG")

    adapter = MockAIAdapter()
    result = adapter.analyze_image(
        buffer.getvalue(), instructions="cuente circulos", content_type="image/png"
    )
    assert result.count == 0
    assert any("ilegible" in w for w in result.warnings)


def test_mock_adapter_analyze_image_does_not_warn_on_legitimate_empty_scene():
    # Regresion: antes se advertia "no se detectaron objetos" para cualquier
    # conteo 0, confundiendo una escena vacia (resultado valido) con una
    # imagen ilegible — la guia exige que la escena vacia no produzca aviso.
    blank = Image.new("RGB", (100, 100), color=(255, 255, 255))
    buffer = io.BytesIO()
    blank.save(buffer, format="PNG")

    adapter = MockAIAdapter()
    result = adapter.analyze_image(
        buffer.getvalue(), instructions="cuente circulos", content_type="image/png"
    )
    assert result.count == 0
    assert result.warnings == []


def test_mock_adapter_analyze_image_warns_on_empty_bytes():
    adapter = MockAIAdapter()
    result = adapter.analyze_image(b"", instructions="cuente circulos", content_type="image/png")
    assert result.count == 0
    assert result.warnings


def test_mock_adapter_analyze_image_counts_circles():
    adapter = MockAIAdapter()
    result = adapter.analyze_image(
        _draw_circles(5), instructions="cuente circulos", content_type="image/png"
    )
    assert result.count == 5
    assert result.warnings == []


def test_mock_adapter_analyze_image_warns_on_corrupt_bytes():
    adapter = MockAIAdapter()
    result = adapter.analyze_image(
        b"not-an-image", instructions="cuente circulos", content_type="image/png"
    )
    assert result.count == 0
    assert "ilegible" in result.warnings[0]


def test_mock_adapter_generate_feedback_reflects_passed_and_failed():
    adapter = MockAIAdapter()
    passed_feedback = adapter.generate_feedback(
        context={"practice_title": "X", "score": 100, "passed": True}
    )
    failed_feedback = adapter.generate_feedback(
        context={"practice_title": "X", "score": 20, "passed": False}
    )
    manual_feedback = adapter.generate_feedback(
        context={"practice_title": "X", "score": 0, "passed": None}
    )
    assert "cumpli" in passed_feedback
    assert "no cumpli" in failed_feedback
    assert "revision manual" in manual_feedback
