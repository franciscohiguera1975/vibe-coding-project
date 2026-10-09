from fastapi import Header, Query

from app.domain.services.practice_localization import DEFAULT_LANGUAGE, SUPPORTED_LANGUAGES


def get_language(
    lang: str | None = Query(default=None, description="Idioma preferido (es|en|pt|fr)"),
    accept_language: str | None = Header(default=None),
) -> str:
    """Resuelve el idioma efectivo de la solicitud: `lang` explicito tiene prioridad
    sobre el primer subtag de `Accept-Language`; si ninguno esta presente o ninguno
    es soportado, cae a espanol ("es"), preservando el comportamiento anterior a la
    localizacion de practicas."""
    candidate = lang or (accept_language.split(",")[0].strip() if accept_language else None)
    if not candidate:
        return DEFAULT_LANGUAGE

    normalized = candidate.split("-")[0].strip().lower()
    return normalized if normalized in SUPPORTED_LANGUAGES else DEFAULT_LANGUAGE
