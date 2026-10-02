from pydantic import BaseModel


class PermissionPublic(BaseModel):
    code: str
    description: str


class RolePublic(BaseModel):
    id: str
    name: str
    description: str
    permissions: list[PermissionPublic]


class AssignPermissionRequest(BaseModel):
    permission_code: str
