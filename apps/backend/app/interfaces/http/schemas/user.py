from pydantic import BaseModel, EmailStr, Field

from app.interfaces.http.schemas.auth import UserPublic


class CreateUserRequest(BaseModel):
    email: EmailStr
    full_name: str = Field(min_length=1, max_length=255)
    password: str = Field(min_length=8, max_length=72)
    role_names: list[str] = Field(default_factory=list)


class AssignRoleRequest(BaseModel):
    role_name: str


class UserListResponse(BaseModel):
    items: list[UserPublic]
    total: int
    page: int
    page_size: int
    total_pages: int


__all__ = ["CreateUserRequest", "AssignRoleRequest", "UserListResponse", "UserPublic"]
