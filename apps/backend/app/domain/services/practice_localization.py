"""Localizacion de practicas (campos pedagogicos: titulo, descripcion, objetivos,
instrucciones y `content`). El espanol (`Practice.title`, etc.) es siempre el
contenido base/fuente de verdad; `Practice.translations` guarda, por idioma, solo
las claves que difieren del espanol (overlay parcial) — ver
database/seeds/practices_data.py y el Prompt Maestro §16/§37.

Resolver el idioma efectivo (query param / header Accept-Language) es
responsabilidad de la capa HTTP (ver
app.interfaces.http.dependencies.localization); este modulo solo sabe fusionar una
Practice con una traduccion ya resuelta, sin IO ni dependencias de framework."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.domain.entities.practice import Practice

DEFAULT_LANGUAGE = "es"
SUPPORTED_LANGUAGES = ("es", "en", "pt", "fr")


@dataclass(frozen=True, slots=True)
class LocalizedPracticeContent:
    """Los campos de una practica ya resueltos para un idioma concreto."""

    title: str
    description: str
    objectives: list[str]
    instructions: str
    content: dict[str, Any]


def _deep_merge(base: Any, overlay: Any) -> Any:
    """Superpone `overlay` sobre `base`. Si ambos son dict se fusionan clave a clave
    (recursivo); en cualquier otro caso (listas, escalares) `overlay` reemplaza a
    `base` por completo cuando esta presente. Una clave ausente en `overlay` nunca
    borra la clave base: simplemente no se toca."""
    if isinstance(base, dict) and isinstance(overlay, dict):
        merged = dict(base)
        for key, value in overlay.items():
            merged[key] = _deep_merge(base.get(key), value) if key in base else value
        return merged
    return overlay


def localize_practice(practice: Practice, lang: str | None) -> LocalizedPracticeContent:
    """Devuelve los campos efectivos de `practice` para `lang`.

    - `lang` None, vacio, "es", o sin entrada en `translations`: se devuelven los
      campos en espanol tal cual (comportamiento identico al anterior a esta
      funcionalidad).
    - En otro caso se superpone `translations[lang]` sobre la base espanola, campo
      por campo: una traduccion parcial (p.ej. solo `title` e `instructions`) cae de
      vuelta al espanol en los campos que no tradujo — nunca se deja un campo vacio
      ni se mezcla un idioma con una cadena vacia.
    """
    base = LocalizedPracticeContent(
        title=practice.title,
        description=practice.description,
        objectives=list(practice.objectives),
        instructions=practice.instructions,
        content=dict(practice.content),
    )

    if not lang or lang == DEFAULT_LANGUAGE:
        return base

    translation = practice.translations.get(lang)
    if not translation:
        return base

    return LocalizedPracticeContent(
        title=translation.get("title", base.title),
        description=translation.get("description", base.description),
        objectives=translation.get("objectives", base.objectives),
        instructions=translation.get("instructions", base.instructions),
        content=_deep_merge(base.content, translation.get("content", {})),
    )
