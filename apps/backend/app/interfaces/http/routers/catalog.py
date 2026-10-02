from collections.abc import Callable

from fastapi import APIRouter, Depends

from app.application.ports.unit_of_work import UnitOfWork
from app.application.use_cases.catalog.manage_catalog import (
    CreatePracticeCategoryUseCase,
    CreatePracticeTagUseCase,
)
from app.domain import permissions as perm
from app.domain.entities.identity import User
from app.interfaces.http.controllers.catalog_controller import category_to_public, tag_to_public
from app.interfaces.http.dependencies.admin_use_cases import (
    get_create_category_use_case,
    get_create_tag_use_case,
)
from app.interfaces.http.dependencies.auth import require_permission
from app.interfaces.http.dependencies.unit_of_work import get_uow_factory
from app.interfaces.http.schemas.catalog import (
    CreateCategoryRequest,
    CreateTagRequest,
    PracticeCategoryPublic,
    PracticeTagPublic,
)

router = APIRouter(tags=["catalog"])


@router.get("/practice-categories", response_model=list[PracticeCategoryPublic])
def list_categories(
    uow_factory: Callable[[], UnitOfWork] = Depends(get_uow_factory),
) -> list[PracticeCategoryPublic]:
    with uow_factory() as uow:
        categories = uow.practice_categories.list_all()
    return [category_to_public(c) for c in categories]


@router.post("/practice-categories", response_model=PracticeCategoryPublic, status_code=201)
def create_category(
    payload: CreateCategoryRequest,
    actor: User = Depends(require_permission(perm.PRACTICE_CREATE)),
    use_case: CreatePracticeCategoryUseCase = Depends(get_create_category_use_case),
) -> PracticeCategoryPublic:
    category = use_case.execute(actor=actor, name=payload.name, slug=payload.slug)
    return category_to_public(category)


@router.get("/practice-tags", response_model=list[PracticeTagPublic])
def list_tags(
    uow_factory: Callable[[], UnitOfWork] = Depends(get_uow_factory),
) -> list[PracticeTagPublic]:
    with uow_factory() as uow:
        tags = uow.practice_tags.list_all()
    return [tag_to_public(t) for t in tags]


@router.post("/practice-tags", response_model=PracticeTagPublic, status_code=201)
def create_tag(
    payload: CreateTagRequest,
    actor: User = Depends(require_permission(perm.PRACTICE_CREATE)),
    use_case: CreatePracticeTagUseCase = Depends(get_create_tag_use_case),
) -> PracticeTagPublic:
    tag = use_case.execute(actor=actor, name=payload.name)
    return tag_to_public(tag)
