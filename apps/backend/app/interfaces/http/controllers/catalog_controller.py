from app.domain.entities.practice import PracticeCategory, PracticeTag
from app.interfaces.http.schemas.catalog import PracticeCategoryPublic, PracticeTagPublic


def category_to_public(category: PracticeCategory) -> PracticeCategoryPublic:
    return PracticeCategoryPublic(
        id=str(category.id),
        name=category.name,
        slug=category.slug,
        description=category.description,
        parent_id=str(category.parent_id) if category.parent_id else None,
    )


def tag_to_public(tag: PracticeTag) -> PracticeTagPublic:
    return PracticeTagPublic(id=str(tag.id), name=tag.name, slug=tag.slug)
