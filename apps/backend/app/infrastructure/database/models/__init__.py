"""Importa todos los modelos para registrarlos en Base.metadata (Alembic autogenerate y
resolucion de relaciones entre modulos)."""

from app.infrastructure.database.models.ai import (  # noqa: F401
    AIMessageModel,
    AISessionModel,
    AIToolCallModel,
)
from app.infrastructure.database.models.catalog import (  # noqa: F401
    PracticeCategoryModel,
    PracticeTagModel,
)
from app.infrastructure.database.models.identity import (  # noqa: F401
    PermissionModel,
    RoleModel,
    UserModel,
)
from app.infrastructure.database.models.practice import (  # noqa: F401
    PracticeContentModel,
    PracticeModel,
)
from app.infrastructure.database.models.progress import (  # noqa: F401
    PracticeEvaluationModel,
    PracticeSubmissionModel,
    StudentPracticeAttemptModel,
    StudentProgressModel,
)
from app.infrastructure.database.models.system import (  # noqa: F401
    AuditLogModel,
    ConfigurationModel,
)

__all__ = [
    "UserModel",
    "RoleModel",
    "PermissionModel",
    "PracticeCategoryModel",
    "PracticeTagModel",
    "PracticeModel",
    "PracticeContentModel",
    "StudentPracticeAttemptModel",
    "PracticeSubmissionModel",
    "PracticeEvaluationModel",
    "StudentProgressModel",
    "AISessionModel",
    "AIMessageModel",
    "AIToolCallModel",
    "ConfigurationModel",
    "AuditLogModel",
]
