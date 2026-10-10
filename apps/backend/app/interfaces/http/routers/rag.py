from fastapi import APIRouter, Depends

from app.application.use_cases.rag.run_evaluation import RunRagEvaluationUseCase
from app.application.use_cases.rag.validate_syllabus import ValidateSyllabusUseCase
from app.domain import permissions as perm
from app.domain.entities.identity import User
from app.domain.exceptions import NotFoundError
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


@router.post("/validate-syllabus", response_model=list[ChecklistItemResultResponse])
def validate_syllabus(
    payload: ValidateSyllabusRequest,
    actor: User = Depends(get_current_user),
    use_case: ValidateSyllabusUseCase = Depends(get_validate_syllabus_use_case),
) -> list[ChecklistItemResultResponse]:
    results = use_case.execute(actor=actor, syllabus_text=payload.text)
    return [
        ChecklistItemResultResponse(
            item=r.item,
            label=r.label,
            cumple=r.cumple,
            explicacion=r.explicacion,
            citas=[
                CitationRefResponse(source_document=c.source_document, article_label=c.article_label)
                for c in r.citas
            ],
        )
        for r in results
    ]


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
