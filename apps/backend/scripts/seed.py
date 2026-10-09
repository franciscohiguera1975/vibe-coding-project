#!/usr/bin/env python
"""Seed idempotente (Prompt Maestro §18): roles, permisos, usuario admin de desarrollo,
configuraciones, categorias y las 4 practicas iniciales. Re-ejecutable sin duplicar
(cada entidad se busca por su clave natural antes de crearse).

Uso: python scripts/seed.py  (o `make seed`)
Credenciales del admin de desarrollo: ver docs/installation.md / SEED_ADMIN_EMAIL,
SEED_ADMIN_PASSWORD en el entorno (valores por defecto solo para desarrollo local).
"""

import os
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
REPO_ROOT = BACKEND_DIR.parent.parent
sys.path.insert(0, str(BACKEND_DIR))
sys.path.insert(0, str(REPO_ROOT))

from database.seeds.practices_data import INITIAL_PRACTICES  # noqa: E402

from app.domain import permissions as perm  # noqa: E402
from app.domain.entities.identity import Permission, Role, User  # noqa: E402
from app.domain.entities.practice import (  # noqa: E402
    Practice,
    PracticeCategory,
    PracticeDifficulty,
    PracticeStatus,
)
from app.domain.entities.system import Configuration  # noqa: E402
from app.domain.value_objects.slug import Slug  # noqa: E402
from app.infrastructure.database.unit_of_work import SqlAlchemyUnitOfWork  # noqa: E402
from app.infrastructure.security.password_hasher import BcryptPasswordHasher  # noqa: E402

SEED_ADMIN_EMAIL = os.environ.get("SEED_ADMIN_EMAIL", "admin@vibecoding-platform.dev")
SEED_ADMIN_PASSWORD = os.environ.get("SEED_ADMIN_PASSWORD", "ChangeMe123!")

CATEGORIES = [
    {"name": "Desarrollo de Software", "slug": "desarrollo-de-software"},
    {"name": "Manejo de Imágenes", "slug": "manejo-de-imagenes"},
]

DEFAULT_CONFIGURATIONS = [
    {
        "key": "platform.name",
        "value": {"value": "Vibe Coding Platform"},
        "description": "Nombre publico de la plataforma",
    },
    {
        "key": "ai.default_provider",
        "value": {"value": "mock"},
        "description": "Proveedor de IA por defecto (mock|anthropic), ver AI_PROVIDER",
    },
]


def seed_permissions(uow) -> dict[str, Permission]:
    result = {}
    for code, description in perm.ALL_PERMISSIONS.items():
        existing = uow.permissions.get_by_code(code)
        result[code] = existing or uow.permissions.add(
            Permission(code=code, description=description)
        )
    return result


def seed_roles(uow, permissions_by_code: dict[str, Permission]) -> dict[str, Role]:
    """Crea los roles faltantes y sincroniza los permisos de ROLE_DEFINITIONS en los ya
    existentes (re-ejecutar el seed despues de agregar un permiso nuevo debe propagarlo)."""
    result = {}
    for role_name, codes in perm.ROLE_DEFINITIONS.items():
        role_permissions = [permissions_by_code[c] for c in codes]
        existing = uow.roles.get_by_name(role_name)
        if existing:
            existing_codes = {p.code for p in existing.permissions}
            if existing_codes != set(codes):
                existing.permissions = role_permissions
                existing = uow.roles.update(existing)
            result[role_name] = existing
            continue
        result[role_name] = uow.roles.add(
            Role(name=role_name, description=f"Rol {role_name}", permissions=role_permissions)
        )
    return result


def seed_admin_user(uow, hasher: BcryptPasswordHasher, roles_by_name: dict[str, Role]) -> User:
    existing = uow.users.get_by_email(SEED_ADMIN_EMAIL)
    if existing:
        return existing
    return uow.users.add(
        User(
            email=SEED_ADMIN_EMAIL,
            password_hash=hasher.hash(SEED_ADMIN_PASSWORD),
            full_name="Administrador (desarrollo)",
            roles=[roles_by_name["ADMIN"]],
        )
    )


def seed_configurations(uow) -> None:
    for entry in DEFAULT_CONFIGURATIONS:
        if uow.configurations.get_by_key(entry["key"]) is not None:
            continue
        uow.configurations.upsert(
            Configuration(key=entry["key"], value=entry["value"], description=entry["description"])
        )


def seed_categories(uow) -> dict[str, PracticeCategory]:
    result = {}
    for cat in CATEGORIES:
        existing = uow.practice_categories.get_by_slug(cat["slug"])
        result[cat["slug"]] = existing or uow.practice_categories.add(
            PracticeCategory(name=cat["name"], slug=cat["slug"])
        )
    return result


def seed_practices(uow, admin: User, categories_by_slug: dict[str, PracticeCategory]) -> None:
    for entry in INITIAL_PRACTICES:
        translations = entry.get("translations", {})
        existing = uow.practices.get_by_slug(entry["slug"])
        if existing is not None:
            # Re-ejecutar el seed despues de agregar/editar traducciones debe
            # propagarlas a practicas ya sembradas, sin tocar el resto de sus campos
            # (que pueden haber sido editados desde el panel de administracion).
            if existing.translations != translations:
                existing.translations = translations
                uow.practices.update(existing)
            continue

        tags = [
            uow.practice_tags.get_or_create(name=name, slug=str(Slug.from_text(name)))
            for name in entry.get("tags", [])
        ]
        category = categories_by_slug.get(entry["category_slug"])

        practice = Practice(
            slug=entry["slug"],
            title=entry["title"],
            type=entry["type"],
            description=entry["description"],
            objectives=entry["objectives"],
            instructions=entry["instructions"],
            category_id=category.id if category else None,
            difficulty=PracticeDifficulty(entry["difficulty"]),
            estimated_time_minutes=entry["estimated_time_minutes"],
            technologies=entry["technologies"],
            tag_ids=[t.id for t in tags],
            content=entry["content"],
            evaluation=entry["evaluation"],
            ai_configuration=entry.get("ai_configuration", {}),
            embedding_configuration=entry.get("embedding_configuration", {}),
            status=PracticeStatus(entry["status"]),
            metadata=entry.get("metadata", {}),
            translations=translations,
            created_by_id=admin.id,
        )
        uow.practices.add(practice)


def main() -> None:
    hasher = BcryptPasswordHasher()
    with SqlAlchemyUnitOfWork() as uow:
        permissions_by_code = seed_permissions(uow)
        roles_by_name = seed_roles(uow, permissions_by_code)
        admin = seed_admin_user(uow, hasher, roles_by_name)
        seed_configurations(uow)
        categories_by_slug = seed_categories(uow)
        seed_practices(uow, admin, categories_by_slug)
        uow.commit()

    print("Seed completado.")
    print(f"Admin de desarrollo: {SEED_ADMIN_EMAIL} / {SEED_ADMIN_PASSWORD}")
    print(
        "Cambie estas credenciales antes de cualquier despliegue real (ver docs/installation.md)."
    )


if __name__ == "__main__":
    main()
