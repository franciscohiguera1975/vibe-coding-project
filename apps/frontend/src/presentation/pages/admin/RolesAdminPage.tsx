import { useAssignPermission, usePermissions, useRoles } from '@/application/hooks/use-admin';

export function RolesAdminPage() {
  const { data: roles, isLoading } = useRoles();
  const { data: permissions } = usePermissions();
  const assignPermission = useAssignPermission();

  return (
    <div>
      <h1 className="text-2xl font-semibold text-ink-900">Roles y permisos</h1>
      <p className="mt-1 text-sm text-ink-500">
        Cada rol agrupa permisos. Asigne un permiso adicional a un rol si lo necesita.
      </p>

      <div className="mt-6 grid grid-cols-1 gap-4 lg:grid-cols-2">
        {isLoading && <p className="text-sm text-ink-500">Cargando...</p>}
        {roles?.map((role) => (
          <div key={role.id} className="card p-5">
            <div className="flex items-center justify-between">
              <h2 className="font-semibold text-ink-900">{role.name}</h2>
              <select
                className="input w-auto"
                defaultValue=""
                onChange={(e) => {
                  if (e.target.value) {
                    assignPermission.mutate({
                      roleName: role.name,
                      permissionCode: e.target.value,
                    });
                    e.target.value = '';
                  }
                }}
              >
                <option value="" disabled>
                  Agregar permiso...
                </option>
                {permissions
                  ?.filter((p) => !role.permissions.some((rp) => rp.code === p.code))
                  .map((p) => (
                    <option key={p.code} value={p.code}>
                      {p.code}
                    </option>
                  ))}
              </select>
            </div>
            <div className="mt-3 flex flex-wrap gap-1">
              {role.permissions.map((permission) => (
                <span key={permission.code} className="badge bg-ink-100 text-ink-600">
                  {permission.code}
                </span>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
