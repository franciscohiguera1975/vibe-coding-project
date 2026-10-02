from app.domain.entities.identity import Role
from app.interfaces.http.schemas.role import PermissionPublic, RolePublic


def role_to_public(role: Role) -> RolePublic:
    return RolePublic(
        id=str(role.id),
        name=role.name,
        description=role.description,
        permissions=[
            PermissionPublic(code=p.code, description=p.description) for p in role.permissions
        ],
    )
