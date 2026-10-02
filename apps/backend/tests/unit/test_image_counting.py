import io

from PIL import Image, ImageDraw

from app.infrastructure.ai.image_counting import count_colored_regions
from app.infrastructure.ai.mock_adapter import MockAIAdapter


def _draw_circles(n: int, size: tuple[int, int] = (200, 200)) -> bytes:
    image = Image.new("RGB", size, color=(255, 255, 255))
    draw = ImageDraw.Draw(image)
    colors = [(220, 30, 30), (30, 120, 220), (30, 180, 60), (230, 180, 20)]
    for i in range(n):
        x = 20 + (i % 4) * 45
        y = 20 + (i // 4) * 45
        draw.ellipse([x, y, x + 30, y + 30], fill=colors[i % len(colors)])
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def test_count_colored_regions_matches_number_of_circles():
    image_bytes = _draw_circles(3)
    count, details = count_colored_regions(image_bytes)
    assert count == 3
    assert details["image_size"] == [200, 200]


def test_count_colored_regions_empty_scene_is_zero():
    blank = Image.new("RGB", (100, 100), color=(255, 255, 255))
    buffer = io.BytesIO()
    blank.save(buffer, format="PNG")
    count, _ = count_colored_regions(buffer.getvalue())
    assert count == 0


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
