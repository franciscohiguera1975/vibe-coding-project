from pydantic import BaseModel, Field


class PracticeCategoryPublic(BaseModel):
    id: str
    name: str
    slug: str
    description: str
    parent_id: str | None


class CreateCategoryRequest(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    slug: str | None = None


class PracticeTagPublic(BaseModel):
    id: str
    name: str
    slug: str


class CreateTagRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
