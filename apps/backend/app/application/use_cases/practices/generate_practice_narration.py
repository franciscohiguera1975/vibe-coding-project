import hashlib
from collections.abc import Callable
from dataclasses import dataclass

from app.application.ports.narration import NarrationPort
from app.application.ports.storage import StoragePort
from app.application.ports.unit_of_work import UnitOfWork
from app.application.services import audit
from app.domain import permissions as perm
from app.domain.entities.identity import User
from app.domain.entities.practice import PracticeNarration
from app.domain.exceptions import NotFoundError, PermissionDeniedError
from app.domain.services.practice_localization import LocalizedPracticeContent, localize_practice


@dataclass(frozen=True, slots=True)
class NarrationResult:
    """Resultado de GeneratePracticeNarrationUseCase: el router lo traduce a
    `{lang, url, cached}` usando StoragePort.get_url(storage_key)."""

    lang: str
    storage_key: str
    cached: bool


def build_narration_script(localized: LocalizedPracticeContent) -> str:
    """Compone un guion legible en voz alta a partir del contenido localizado: titulo,
    luego objetivos unidos en una frase, luego instrucciones. No reimplementa
    localizacion (usa el resultado ya resuelto de `localize_practice`)."""
    parts: list[str] = []

    title = localized.title.strip()
    if title:
        parts.append(title if title.endswith((".", "!", "?")) else f"{title}.")

    objectives = [o.strip().rstrip(".") for o in localized.objectives if o.strip()]
    if objectives:
        parts.append("; ".join(objectives) + ".")

    instructions = localized.instructions.strip()
    if instructions:
        parts.append(instructions if instructions.endswith((".", "!", "?")) else f"{instructions}.")

    return " ".join(parts)


class GeneratePracticeNarrationUseCase:
    """GeneratePracticeNarration: sintetiza (o reutiliza, si el texto no cambio) el
    audio narrado de una practica en un idioma concreto. Es la unica via por la que
    el sistema llama a NarrationPort — nunca se dispara automaticamente al ver una
    practica, para controlar el costo de la API externa."""

    def __init__(
        self,
        uow_factory: Callable[[], UnitOfWork],
        narration_port: NarrationPort,
        storage_port: StoragePort,
    ) -> None:
        self._uow_factory = uow_factory
        self._narration_port = narration_port
        self._storage_port = storage_port

    def execute(self, *, actor: User, slug: str, lang: str) -> NarrationResult:
        if not actor.has_permission(perm.PRACTICE_UPDATE):
            raise PermissionDeniedError(perm.PRACTICE_UPDATE)

        with self._uow_factory() as uow:
            practice = uow.practices.get_by_slug(slug)
            if practice is None:
                raise NotFoundError("Practice", slug)

            localized = localize_practice(practice, lang)
            script = build_narration_script(localized)
            text_hash = hashlib.sha256(script.encode("utf-8")).hexdigest()

            existing = uow.practice_narrations.get_by_practice_and_lang(practice.id, lang)
            if existing is not None and existing.text_hash == text_hash:
                # El texto fuente no cambio desde la ultima generacion: devolvemos el
                # audio ya almacenado sin volver a llamar al proveedor de narracion
                # (control de costo, ver Prompt Maestro §10/§20).
                return NarrationResult(lang=lang, storage_key=existing.storage_key, cached=True)

            audio_bytes = self._narration_port.synthesize(script, lang=lang)

            if existing is not None:
                try:
                    self._storage_port.delete(existing.storage_key)
                except Exception:  # noqa: BLE001 - best effort, nunca debe romper la regeneracion
                    pass

            storage_key = self._storage_port.upload(
                audio_bytes,
                filename=f"{practice.slug}-{lang}.mp3",
                content_type="audio/mpeg",
            )

            saved = uow.practice_narrations.upsert(
                PracticeNarration(
                    practice_id=practice.id,
                    lang=lang,
                    storage_key=storage_key,
                    text_hash=text_hash,
                )
            )
            audit.record(
                uow,
                actor=actor,
                action="practice.narration.generate",
                entity_type="Practice",
                entity_id=str(practice.id),
                metadata={"slug": practice.slug, "lang": lang},
            )
            uow.commit()
            return NarrationResult(lang=lang, storage_key=saved.storage_key, cached=False)
