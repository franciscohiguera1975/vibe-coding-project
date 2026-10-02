from app.domain.entities.identity import User
from app.domain.value_objects.pagination import Page
from app.interfaces.http.controllers.auth_controller import user_to_public
from app.interfaces.http.schemas.user import UserListResponse


def user_page_to_response(page: Page[User]) -> UserListResponse:
    return UserListResponse(
        items=[user_to_public(u) for u in page.items],
        total=page.total,
        page=page.page,
        page_size=page.page_size,
        total_pages=page.total_pages,
    )
