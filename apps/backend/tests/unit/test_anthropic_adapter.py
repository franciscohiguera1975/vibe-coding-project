import json
from unittest.mock import MagicMock, patch

from app.infrastructure.ai.anthropic_adapter import AnthropicAdapter


def _text_block(text: str) -> MagicMock:
    block = MagicMock()
    block.type = "text"
    block.text = text
    return block


@patch("app.infrastructure.ai.anthropic_adapter.Anthropic")
def test_generate_text_calls_messages_create_and_joins_text_blocks(mock_anthropic_cls):
    mock_client = MagicMock()
    mock_anthropic_cls.return_value = mock_client
    mock_client.messages.create.return_value = MagicMock(content=[_text_block("hola")])

    adapter = AnthropicAdapter(api_key="test-key", model="claude-test")
    result = adapter.generate_text("di hola", system="eres breve", max_tokens=50)

    assert result == "hola"
    mock_client.messages.create.assert_called_once_with(
        model="claude-test",
        max_tokens=50,
        system="eres breve",
        messages=[{"role": "user", "content": "di hola"}],
    )


@patch("app.infrastructure.ai.anthropic_adapter.Anthropic")
def test_analyze_image_parses_structured_json_response(mock_anthropic_cls):
    mock_client = MagicMock()
    mock_anthropic_cls.return_value = mock_client
    payload = {
        "count": 4,
        "confidence": 0.8,
        "reason": "cuatro circulos visibles",
        "illegible": False,
    }
    mock_client.messages.create.return_value = MagicMock(content=[_text_block(json.dumps(payload))])

    adapter = AnthropicAdapter(api_key="test-key", model="claude-test")
    result = adapter.analyze_image(
        b"fake-bytes", instructions="cuente circulos", content_type="image/png"
    )

    assert result.count == 4
    assert result.warnings == []
    assert result.details["confidence"] == 0.8


@patch("app.infrastructure.ai.anthropic_adapter.Anthropic")
def test_analyze_image_treats_illegible_as_zero_count(mock_anthropic_cls):
    mock_client = MagicMock()
    mock_anthropic_cls.return_value = mock_client
    payload = {"count": 7, "confidence": 0.1, "reason": "borrosa", "illegible": True}
    mock_client.messages.create.return_value = MagicMock(content=[_text_block(json.dumps(payload))])

    adapter = AnthropicAdapter(api_key="test-key", model="claude-test")
    result = adapter.analyze_image(
        b"fake-bytes", instructions="cuente circulos", content_type="image/png"
    )

    assert result.count == 0
    assert result.warnings == ["imagen ilegible"]


@patch("app.infrastructure.ai.anthropic_adapter.Anthropic")
def test_analyze_image_handles_unparseable_response(mock_anthropic_cls):
    mock_client = MagicMock()
    mock_anthropic_cls.return_value = mock_client
    mock_client.messages.create.return_value = MagicMock(content=[_text_block("no es json")])

    adapter = AnthropicAdapter(api_key="test-key", model="claude-test")
    result = adapter.analyze_image(
        b"fake-bytes", instructions="cuente circulos", content_type="image/png"
    )

    assert result.count == 0
    assert result.warnings
