# Autorización (RBAC)

Modelo clásico usuario → roles → permisos, centralizado en
`app/domain/permissions.py` (única fuente de verdad, consumida tanto por el seed
como por `require_permission`).

## Roles iniciales

| Rol | Permisos |
|---|---|
| `ADMIN` | todos |
| `CONTENT_MANAGER` | `practice:create`, `practice:read`, `practice:update`, `practice:delete`, `practice:publish` |
| `TEACHER` | `practice:read`, `user:read` |
| `STUDENT` | `practice:read` |

## Catálogo de permisos

`practice:create` · `practice:read` · `practice:update` · `practice:delete` ·
`practice:publish` · `user:create` · `user:read` · `user:update` ·
`user:delete` · `configuration:read` · `configuration:update` ·
`role:assign_permission` · `audit:read`.

Los del Prompt Maestro §15 son de ejemplo (no exhaustivos); `practice:publish` y
los de rol/configuración se agregaron porque los usan casos de uso concretos
(`PublishPractice`, `AssignRole`, `AssignPermission`, `ManageConfiguration`).

## Backend: `require_permission`

```python
@router.post("", dependencies=[Depends(require_permission(PRACTICE_CREATE))])
```

`require_permission(code)` es una dependencia FastAPI que reutiliza
`get_current_user` y comprueba `user.has_permission(code)` (método de la entidad
de dominio `User`, calculado sobre sus roles cargados); si falta, responde `403`.

## Frontend: `hasPermission` y `ProtectedRoute`

El login/`/auth/me` devuelve `permissions: string[]` ya aplanado desde los roles
del usuario (`UserPublic.permissions`, calculado en el backend como
`{p.code for role in user.roles for p in role.permissions}`) — el frontend no
necesita conocer la jerarquía rol→permiso, solo comprobar códigos de permiso
directamente:

```tsx
<ProtectedRoute requirePermission="practice:create">...</ProtectedRoute>
```

Esto es **solo para mostrar/ocultar UI** — el backend vuelve a verificar cada
permiso de forma independiente en el endpoint correspondiente; el frontend nunca
es la única barrera de autorización.
