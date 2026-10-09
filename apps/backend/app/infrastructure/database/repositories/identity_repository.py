import uuid

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session, selectinload

from app.domain.entities.identity import PasswordResetToken, Permission, Role, User
from app.domain.value_objects.pagination import Page, PageRequest
from app.infrastructure.database.base import utcnow
from app.infrastructure.database.models.identity import (
    PasswordResetTokenModel,
    PermissionModel,
    RoleModel,
    UserModel,
)


def _permission_to_domain(model: PermissionModel) -> Permission:
    return Permission(id=model.id, code=model.code, description=model.description)


def _role_to_domain(model: RoleModel) -> Role:
    return Role(
        id=model.id,
        name=model.name,
        description=model.description,
        permissions=[_permission_to_domain(p) for p in model.permissions],
    )


def _user_to_domain(model: UserModel) -> User:
    return User(
        id=model.id,
        email=model.email,
        password_hash=model.password_hash,
        full_name=model.full_name,
        is_active=model.is_active,
        roles=[_role_to_domain(r) for r in model.roles],
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


class SqlAlchemyUserRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def _base_query(self):
        return select(UserModel).options(
            selectinload(UserModel.roles).selectinload(RoleModel.permissions)
        )

    def get_by_id(self, user_id: uuid.UUID) -> User | None:
        model = self._session.scalar(self._base_query().where(UserModel.id == user_id))
        return _user_to_domain(model) if model else None

    def get_by_email(self, email: str) -> User | None:
        model = self._session.scalar(self._base_query().where(UserModel.email == email))
        return _user_to_domain(model) if model else None

    def add(self, user: User) -> User:
        role_models = []
        if user.roles:
            role_ids = [r.id for r in user.roles]
            role_models = list(
                self._session.scalars(select(RoleModel).where(RoleModel.id.in_(role_ids)))
            )
        model = UserModel(
            email=user.email,
            password_hash=user.password_hash,
            full_name=user.full_name,
            is_active=user.is_active,
            roles=role_models,
        )
        self._session.add(model)
        self._session.flush()
        self._session.refresh(model, attribute_names=["roles"])
        return _user_to_domain(model)

    def update(self, user: User) -> User:
        model = self._session.get(UserModel, user.id)
        if model is None:
            raise ValueError(f"UserModel {user.id} no encontrado")
        model.email = user.email
        model.password_hash = user.password_hash
        model.full_name = user.full_name
        model.is_active = user.is_active
        if user.roles:
            role_ids = [r.id for r in user.roles]
            model.roles = list(
                self._session.scalars(select(RoleModel).where(RoleModel.id.in_(role_ids)))
            )
        self._session.flush()
        return _user_to_domain(model)

    def list(self, page_request: PageRequest) -> Page[User]:
        total = self._session.scalar(select(func.count()).select_from(UserModel)) or 0
        rows = self._session.scalars(
            self._base_query()
            .order_by(UserModel.created_at.desc())
            .offset(page_request.offset)
            .limit(page_request.page_size)
        )
        return Page(
            items=[_user_to_domain(m) for m in rows],
            total=total,
            page=page_request.page,
            page_size=page_request.page_size,
        )


class SqlAlchemyRoleRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def _base_query(self):
        return select(RoleModel).options(selectinload(RoleModel.permissions))

    def get_by_id(self, role_id: uuid.UUID) -> Role | None:
        model = self._session.scalar(self._base_query().where(RoleModel.id == role_id))
        return _role_to_domain(model) if model else None

    def get_by_name(self, name: str) -> Role | None:
        model = self._session.scalar(self._base_query().where(RoleModel.name == name))
        return _role_to_domain(model) if model else None

    def list_all(self) -> list[Role]:
        rows = self._session.scalars(self._base_query().order_by(RoleModel.name))
        return [_role_to_domain(m) for m in rows]

    def add(self, role: Role) -> Role:
        permission_models = []
        if role.permissions:
            ids = [p.id for p in role.permissions]
            permission_models = list(
                self._session.scalars(select(PermissionModel).where(PermissionModel.id.in_(ids)))
            )
        model = RoleModel(
            name=role.name, description=role.description, permissions=permission_models
        )
        self._session.add(model)
        self._session.flush()
        self._session.refresh(model, attribute_names=["permissions"])
        return _role_to_domain(model)

    def update(self, role: Role) -> Role:
        model = self._session.get(RoleModel, role.id)
        if model is None:
            raise ValueError(f"RoleModel {role.id} no encontrado")
        model.name = role.name
        model.description = role.description
        ids = [p.id for p in role.permissions]
        model.permissions = list(
            self._session.scalars(select(PermissionModel).where(PermissionModel.id.in_(ids)))
        )
        self._session.flush()
        return _role_to_domain(model)


class SqlAlchemyPermissionRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_code(self, code: str) -> Permission | None:
        model = self._session.scalar(select(PermissionModel).where(PermissionModel.code == code))
        return _permission_to_domain(model) if model else None

    def list_all(self) -> list[Permission]:
        rows = self._session.scalars(select(PermissionModel).order_by(PermissionModel.code))
        return [_permission_to_domain(m) for m in rows]

    def add(self, permission: Permission) -> Permission:
        model = PermissionModel(code=permission.code, description=permission.description)
        self._session.add(model)
        self._session.flush()
        return _permission_to_domain(model)


def _password_reset_token_to_domain(model: PasswordResetTokenModel) -> PasswordResetToken:
    return PasswordResetToken(
        id=model.id,
        user_id=model.user_id,
        token_hash=model.token_hash,
        expires_at=model.expires_at,
        used_at=model.used_at,
        created_at=model.created_at,
    )


class SqlAlchemyPasswordResetTokenRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, token: PasswordResetToken) -> PasswordResetToken:
        model = PasswordResetTokenModel(
            user_id=token.user_id, token_hash=token.token_hash, expires_at=token.expires_at
        )
        self._session.add(model)
        self._session.flush()
        return _password_reset_token_to_domain(model)

    def get_by_token_hash(self, token_hash: str) -> PasswordResetToken | None:
        model = self._session.scalar(
            select(PasswordResetTokenModel).where(PasswordResetTokenModel.token_hash == token_hash)
        )
        return _password_reset_token_to_domain(model) if model else None

    def mark_used(self, token_id: uuid.UUID) -> None:
        model = self._session.get(PasswordResetTokenModel, token_id)
        if model is not None:
            model.used_at = utcnow()
            self._session.flush()

    def delete_for_user(self, user_id: uuid.UUID) -> None:
        self._session.execute(
            delete(PasswordResetTokenModel).where(PasswordResetTokenModel.user_id == user_id)
        )
