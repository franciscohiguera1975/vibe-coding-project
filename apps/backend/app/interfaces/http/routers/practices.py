import uuid

from fastapi import APIRouter, Depends, Query

from app.application.dto.practice_dto import CreatePracticeInput, UpdatePracticeInput
from app.application.ports.storage import StoragePort
from app.application.use_cases.practices.create_practice import CreatePracticeUseCase
from app.application.use_cases.practices.evaluate_practice import EvaluatePracticeUseCase
from app.application.use_cases.practices.generate_practice_narration import (
    GeneratePracticeNarrationUseCase,
)
from app.application.use_cases.practices.get_practice import GetPracticeUseCase
from app.application.use_cases.practices.get_practice_narration import (
    GetPracticeNarrationUseCase,
)
from app.application.use_cases.practices.list_practices import ListPracticesUseCase
from app.application.use_cases.practices.publish_practice import PublishPracticeUseCase
from app.application.use_cases.practices.start_practice import StartPracticeUseCase
from app.application.use_cases.practices.submit_practice import SubmitPracticeUseCase
from app.application.use_cases.practices.update_practice import UpdatePracticeUseCase
from app.domain import permissions as perm
from app.domain.entities.identity import User
from app.domain.entities.practice import PracticeDifficulty, PracticeStatus
from app.domain.repositories.practice_repository import PracticeFilters
from app.domain.services.practice_localization import SUPPORTED_LANGUAGES
from app.domain.value_objects.pagination import PageRequest
from app.interfaces.http.controllers.practice_controller import (
    attempt_to_response,
    evaluation_to_response,
    page_to_response,
    practice_to_admin_detail,
    practice_to_detail,
    submission_to_response,
)
from app.interfaces.http.dependencies.auth import (
    get_current_user,
    get_current_user_optional,
    require_permission,
)
from app.interfaces.http.dependencies.localization import get_language
from app.interfaces.http.dependencies.practice_use_cases import (
    get_create_practice_use_case,
    get_evaluate_practice_use_case,
    get_generate_practice_narration_use_case,
    get_get_practice_narration_use_case,
    get_get_practice_use_case,
    get_list_practices_use_case,
    get_publish_practice_use_case,
    get_start_practice_use_case,
    get_submit_practice_use_case,
    get_update_practice_use_case,
)
from app.interfaces.http.dependencies.storage import get_storage_port
from app.interfaces.http.schemas.practice import (
    AttemptResponse,
    CreatePracticeRequest,
    EvaluationResponse,
    NarrationGenerateAllItem,
    NarrationPublicResponse,
    NarrationResponse,
    PracticeAdminDetail,
    PracticeDetail,
    PracticeListResponse,
    SubmissionResponse,
    SubmitPracticeRequest,
    UpdatePracticeRequest,
)

router = APIRouter(prefix="/practices", tags=["practices"])


@router.get("", response_model=PracticeListResponse)
def list_practices(
    category_id: uuid.UUID | None = None,
    difficulty: PracticeDifficulty | None = None,
    technology: str | None = None,
    type: str | None = None,
    status: PracticeStatus | None = None,
    has_ai: bool | None = None,
    search: str | None = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    lang: str = Depends(get_language),
    actor: User | None = Depends(get_current_user_optional),
    use_case: ListPracticesUseCase = Depends(get_list_practices_use_case),
) -> PracticeListResponse:
    filters = PracticeFilters(
        category_id=category_id,
        difficulty=difficulty,
        technology=technology,
        type=type,
        status=status,
        has_ai=has_ai,
        search=search,
    )
    result = use_case.execute(
        actor=actor, filters=filters, page_request=PageRequest(page=page, page_size=page_size)
    )
    return page_to_response(result, lang)


@router.get("/{slug}", response_model=PracticeDetail)
def get_practice(
    slug: str,
    lang: str = Depends(get_language),
    actor: User | None = Depends(get_current_user_optional),
    use_case: GetPracticeUseCase = Depends(get_get_practice_use_case),
) -> PracticeDetail:
    practice = use_case.execute(slug=slug, actor=actor)
    return practice_to_detail(practice, lang)


@router.post("", response_model=PracticeAdminDetail, status_code=201)
def create_practice(
    payload: CreatePracticeRequest,
    actor: User = Depends(require_permission(perm.PRACTICE_CREATE)),
    use_case: CreatePracticeUseCase = Depends(get_create_practice_use_case),
) -> PracticeAdminDetail:
    practice = use_case.execute(
        actor=actor,
        data=CreatePracticeInput(
            title=payload.title,
            type=payload.type,
            slug=payload.slug,
            description=payload.description,
            objectives=payload.objectives,
            instructions=payload.instructions,
            category_slug=payload.category_slug,
            difficulty=payload.difficulty,
            estimated_time_minutes=payload.estimated_time_minutes,
            technologies=payload.technologies,
            tag_names=payload.tag_names,
            content=payload.content,
            evaluation=payload.evaluation,
            ai_configuration=payload.ai_configuration,
            embedding_configuration=payload.embedding_configuration,
            metadata=payload.metadata,
            translations=payload.translations,
        ),
    )
    return practice_to_admin_detail(practice)


@router.patch("/{practice_id}", response_model=PracticeAdminDetail)
def update_practice(
    practice_id: uuid.UUID,
    payload: UpdatePracticeRequest,
    actor: User = Depends(require_permission(perm.PRACTICE_UPDATE)),
    use_case: UpdatePracticeUseCase = Depends(get_update_practice_use_case),
) -> PracticeAdminDetail:
    practice = use_case.execute(
        actor=actor,
        practice_id=practice_id,
        data=UpdatePracticeInput(**payload.model_dump(exclude_unset=True)),
    )
    return practice_to_admin_detail(practice)


@router.post("/{practice_id}/publish", response_model=PracticeAdminDetail)
def publish_practice(
    practice_id: uuid.UUID,
    actor: User = Depends(require_permission(perm.PRACTICE_PUBLISH)),
    use_case: PublishPracticeUseCase = Depends(get_publish_practice_use_case),
) -> PracticeAdminDetail:
    practice = use_case.execute(actor=actor, practice_id=practice_id)
    return practice_to_admin_detail(practice)


@router.post("/{slug}/start", response_model=AttemptResponse)
def start_practice(
    slug: str,
    actor: User = Depends(get_current_user),
    use_case: StartPracticeUseCase = Depends(get_start_practice_use_case),
) -> AttemptResponse:
    attempt = use_case.execute(actor=actor, practice_slug=slug)
    return attempt_to_response(attempt)


@router.post("/attempts/submit", response_model=SubmissionResponse)
def submit_practice(
    payload: SubmitPracticeRequest,
    actor: User = Depends(get_current_user),
    use_case: SubmitPracticeUseCase = Depends(get_submit_practice_use_case),
) -> SubmissionResponse:
    submission = use_case.execute(
        actor=actor, attempt_id=uuid.UUID(payload.attempt_id), payload=payload.payload
    )
    return submission_to_response(submission)


@router.post("/submissions/{submission_id}/evaluate", response_model=EvaluationResponse)
def evaluate_practice(
    submission_id: uuid.UUID,
    actor: User = Depends(get_current_user),
    use_case: EvaluatePracticeUseCase = Depends(get_evaluate_practice_use_case),
) -> EvaluationResponse:
    evaluation = use_case.execute(actor=actor, submission_id=submission_id)
    return evaluation_to_response(evaluation)


@router.post("/{slug}/narration", response_model=NarrationResponse)
def generate_practice_narration(
    slug: str,
    lang: str = Query(..., description="Idioma a narrar (es|en|pt|fr)"),
    actor: User = Depends(require_permission(perm.PRACTICE_UPDATE)),
    use_case: GeneratePracticeNarrationUseCase = Depends(get_generate_practice_narration_use_case),
    storage_port: StoragePort = Depends(get_storage_port),
) -> NarrationResponse:
    result = use_case.execute(actor=actor, slug=slug, lang=lang)
    return NarrationResponse(
        lang=result.lang, url=storage_port.get_url(result.storage_key), cached=result.cached
    )


@router.post("/{slug}/narration/generate-all", response_model=list[NarrationGenerateAllItem])
def generate_all_practice_narrations(
    slug: str,
    actor: User = Depends(require_permission(perm.PRACTICE_UPDATE)),
    use_case: GeneratePracticeNarrationUseCase = Depends(get_generate_practice_narration_use_case),
    storage_port: StoragePort = Depends(get_storage_port),
) -> list[NarrationGenerateAllItem]:
    results: list[NarrationGenerateAllItem] = []
    for lang in SUPPORTED_LANGUAGES:
        try:
            result = use_case.execute(actor=actor, slug=slug, lang=lang)
        except Exception as exc:  # noqa: BLE001 - un idioma no debe abortar los demas
            results.append(NarrationGenerateAllItem(lang=lang, status="error", message=str(exc)))
            continue
        results.append(
            NarrationGenerateAllItem(
                lang=result.lang,
                status="ok",
                url=storage_port.get_url(result.storage_key),
                cached=result.cached,
            )
        )
    return results


@router.get("/{slug}/narration", response_model=NarrationPublicResponse)
def get_practice_narration(
    slug: str,
    lang: str = Query(..., description="Idioma de la narracion (es|en|pt|fr)"),
    actor: User | None = Depends(get_current_user_optional),
    use_case: GetPracticeNarrationUseCase = Depends(get_get_practice_narration_use_case),
    storage_port: StoragePort = Depends(get_storage_port),
) -> NarrationPublicResponse:
    narration = use_case.execute(slug=slug, lang=lang, actor=actor)
    return NarrationPublicResponse(url=storage_port.get_url(narration.storage_key))
