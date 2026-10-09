from app.domain.entities.practice import Practice
from app.domain.services.practice_localization import localize_practice


def _practice(**overrides) -> Practice:
    defaults = dict(
        slug="mru-demo",
        title="Simulación de movimiento rectilíneo uniforme",
        type="software",
        description="Descripcion en espanol",
        objectives=["Objetivo 1", "Objetivo 2"],
        instructions="Instrucciones en espanol",
        content={"model": {"formula": "d = v * t"}, "worked_examples": [{"distance_km": 120}]},
        translations={
            "en": {
                "title": "Uniform rectilinear motion simulation",
                "instructions": "Instructions in English",
            },
            "pt": {
                "title": "Simulação de movimento retilíneo uniforme",
                "description": "Descricao em portugues",
                "objectives": ["Objetivo PT 1", "Objetivo PT 2"],
                "instructions": "Instrucoes em portugues",
                "content": {"model": {"formula": "d = v * t"}},
            },
        },
    )
    defaults.update(overrides)
    return Practice(**defaults)


def test_no_lang_returns_spanish_base():
    practice = _practice()
    localized = localize_practice(practice, None)
    assert localized.title == practice.title
    assert localized.description == practice.description
    assert localized.objectives == practice.objectives
    assert localized.instructions == practice.instructions
    assert localized.content == practice.content


def test_lang_es_returns_spanish_base_even_with_translations():
    practice = _practice()
    localized = localize_practice(practice, "es")
    assert localized.title == practice.title
    assert localized.instructions == practice.instructions


def test_lang_without_translation_entry_falls_back_to_spanish():
    practice = _practice(translations={"pt": {"title": "Simulação..."}})
    localized = localize_practice(practice, "en")
    assert localized.title == practice.title
    assert localized.instructions == practice.instructions


def test_full_translation_overrides_all_translated_fields():
    practice = _practice()
    localized = localize_practice(practice, "pt")
    assert localized.title == "Simulação de movimento retilíneo uniforme"
    assert localized.description == "Descricao em portugues"
    assert localized.objectives == ["Objetivo PT 1", "Objetivo PT 2"]
    assert localized.instructions == "Instrucoes em portugues"


def test_partial_translation_falls_back_per_field_not_as_a_whole():
    """translations['en'] solo trae title e instructions (ver fixture _practice): el
    resto de los campos (description, objectives, content) deben caer de vuelta al
    espanol sin quedar vacios ni mezclar un idioma con el otro de forma inconsistente."""
    practice = _practice()
    localized = localize_practice(practice, "en")

    assert localized.title == "Uniform rectilinear motion simulation"
    assert localized.instructions == "Instructions in English"
    # Campos no traducidos: fallback exacto al espanol, nunca vacios.
    assert localized.description == practice.description
    assert localized.objectives == practice.objectives
    assert localized.content == practice.content


def test_content_overlay_deep_merges_and_preserves_untranslated_keys():
    practice = _practice(
        content={
            "model": {
                "formula": "d = v * t",
                "variables": {"speed_kmh": {"label": "Velocidad", "unit": "km/h", "max": 100}},
            },
            "worked_examples": [{"speed_kmh": 60, "time_h": 2, "distance_km": 120}],
        },
        translations={
            "en": {
                "content": {
                    "model": {"variables": {"speed_kmh": {"label": "Speed"}}},
                }
            }
        },
    )
    localized = localize_practice(practice, "en")

    # La etiqueta se tradujo...
    assert localized.content["model"]["variables"]["speed_kmh"]["label"] == "Speed"
    # ...pero la unidad, el maximo y los ejemplos numericos (no traducibles) se
    # preservan exactamente, sin perder equivalencia numerica entre idiomas.
    assert localized.content["model"]["variables"]["speed_kmh"]["unit"] == "km/h"
    assert localized.content["model"]["variables"]["speed_kmh"]["max"] == 100
    assert localized.content["model"]["formula"] == "d = v * t"
    assert localized.content["worked_examples"] == [
        {"speed_kmh": 60, "time_h": 2, "distance_km": 120}
    ]


def test_empty_lang_string_treated_as_default():
    practice = _practice()
    localized = localize_practice(practice, "")
    assert localized.title == practice.title
