from fastapi import APIRouter, Depends, File, UploadFile

from app.application.use_cases.rag.run_evaluation import RunRagEvaluationUseCase
from app.application.use_cases.rag.validate_syllabus import (
    ChecklistItemResult,
    ValidateSyllabusUseCase,
)
from app.domain import permissions as perm
from app.domain.entities.identity import User
from app.domain.exceptions import NotFoundError
from app.infrastructure.config import Settings, get_settings
from app.infrastructure.documents.docx_extraction import validate_and_extract_docx_text
from app.interfaces.http.dependencies.auth import get_current_user, require_permission
from app.interfaces.http.dependencies.rag_use_cases import (
    get_run_rag_evaluation_use_case,
    get_validate_syllabus_use_case,
)
from app.interfaces.http.dependencies.unit_of_work import get_uow_factory
from app.interfaces.http.schemas.rag import (
    ChecklistItemResultResponse,
    CitationRefResponse,
    RagEvaluationRunResponse,
    ValidateSyllabusRequest,
)

router = APIRouter(prefix="/rag", tags=["rag"])


def _to_checklist_response(results: list[ChecklistItemResult]) -> list[ChecklistItemResultResponse]:
    return [
        ChecklistItemResultResponse(
            item=r.item,
            label=r.label,
            cumple=r.cumple,
            explicacion=r.explicacion,
            citas=[
                CitationRefResponse(
                    source_document=c.source_document, article_label=c.article_label
                )
                for c in r.citas
            ],
        )
        for r in results
    ]


@router.post("/validate-syllabus", response_model=list[ChecklistItemResultResponse])
def validate_syllabus(
    payload: ValidateSyllabusRequest,
    actor: User = Depends(get_current_user),
    use_case: ValidateSyllabusUseCase = Depends(get_validate_syllabus_use_case),
) -> list[ChecklistItemResultResponse]:
    results = use_case.execute(actor=actor, syllabus_text=payload.text)
    return _to_checklist_response(results)


@router.post("/validate-syllabus/upload", response_model=list[ChecklistItemResultResponse])
async def validate_syllabus_upload(
    file: UploadFile = File(...),
    actor: User = Depends(get_current_user),
    use_case: ValidateSyllabusUseCase = Depends(get_validate_syllabus_use_case),
    settings: Settings = Depends(get_settings),
) -> list[ChecklistItemResultResponse]:
    file_bytes = await file.read()
    syllabus_text = validate_and_extract_docx_text(
        filename=file.filename or "upload.docx",
        file_bytes=file_bytes,
        max_size_mb=settings.storage_max_upload_mb,
    )
    results = use_case.execute(actor=actor, syllabus_text=syllabus_text)
    return _to_checklist_response(results)


@router.post("/evaluation/run", response_model=RagEvaluationRunResponse)
def run_evaluation(
    actor: User = Depends(require_permission(perm.PRACTICE_UPDATE)),
    use_case: RunRagEvaluationUseCase = Depends(get_run_rag_evaluation_use_case),
) -> RagEvaluationRunResponse:
    run = use_case.execute(actor=actor)
    return RagEvaluationRunResponse(id=str(run.id), results=run.results, summary=run.summary)


@router.get("/evaluation", response_model=RagEvaluationRunResponse)
def get_latest_evaluation(
    uow_factory=Depends(get_uow_factory),
) -> RagEvaluationRunResponse:
    with uow_factory() as uow:
        run = uow.rag_evaluation_runs.get_latest()
    if run is None:
        raise NotFoundError("RagEvaluationRun", "latest")
    return RagEvaluationRunResponse(id=str(run.id), results=run.results, summary=run.summary)
