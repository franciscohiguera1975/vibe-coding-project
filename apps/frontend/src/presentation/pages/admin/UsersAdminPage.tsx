import { useAssignRole, useCreateUser, useRoles, useUsers } from '@/application/hooks/use-admin';
import { FormEvent, useState } from 'react';

export function UsersAdminPage() {
  const [page, setPage] = useState(1);
  const { data, isLoading } = useUsers(page);
  const { data: roles } = useRoles();
  const createUser = useCreateUser();
  const assignRole = useAssignRole();
  const [showForm, setShowForm] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [form, setForm] = useState({ email: '', fullName: '', password: '' });

  async function handleCreate(event: FormEvent) {
    event.preventDefault();
    setError(null);
    try {
      await createUser.mutateAsync(form);
      setShowForm(false);
      setForm({ email: '', fullName: '', password: '' });
    } catch {
      setError('No se pudo crear el usuario (¿el correo ya está registrado?).');
    }
  }

  return (
    <div>
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold text-ink-900">Usuarios</h1>
        <button className="btn-primary" onClick={() => setShowForm((v) => !v)}>
          {showForm ? 'Cancelar' : 'Nuevo usuario'}
        </button>
      </div>

      {showForm && (
        <form onSubmit={handleCreate} className="card mt-4 space-y-3 p-5">
          <div>
            <label className="label">Correo electrónico</label>
            <input
              type="email"
              required
              className="input"
              value={form.email}
              onChange={(e) => setForm((f) => ({ ...f, email: e.target.value }))}
            />
          </div>
          <div>
            <label className="label">Nombre completo</label>
            <input
              required
              className="input"
              value={form.fullName}
              onChange={(e) => setForm((f) => ({ ...f, fullName: e.target.value }))}
            />
          </div>
          <div>
            <label className="label">Contraseña</label>
            <input
              type="password"
              required
              minLength={8}
              className="input"
              value={form.password}
              onChange={(e) => setForm((f) => ({ ...f, password: e.target.value }))}
            />
          </div>
          {error && <p className="text-sm text-rose-600">{error}</p>}
          <button type="submit" className="btn-primary" disabled={createUser.isPending}>
            {createUser.isPending ? 'Creando...' : 'Crear usuario'}
          </button>
        </form>
      )}

      <div className="mt-6 overflow-x-auto">
        {isLoading && <p className="text-sm text-ink-500">Cargando...</p>}
        <table className="w-full min-w-[640px] text-left text-sm">
          <thead>
            <tr className="border-b border-ink-100 text-ink-500">
              <th className="py-2">Nombre</th>
              <th className="py-2">Correo</th>
              <th className="py-2">Roles</th>
              <th className="py-2">Asignar rol</th>
            </tr>
          </thead>
          <tbody>
            {data?.items.map((user) => (
              <tr key={user.id} className="border-b border-ink-50">
                <td className="py-2 font-medium text-ink-900">{user.fullName}</td>
                <td className="py-2 text-ink-500">{user.email}</td>
                <td className="py-2">
                  <div className="flex flex-wrap gap-1">
                    {user.roles.map((role) => (
                      <span key={role} className="badge bg-brand-50 text-brand-700">
                        {role}
                      </span>
                    ))}
                  </div>
                </td>
                <td className="py-2">
                  <select
                    className="input"
                    defaultValue=""
                    onChange={(e) => {
                      if (e.target.value) {
                        assignRole.mutate({ userId: user.id, roleName: e.target.value });
                        e.target.value = '';
                      }
                    }}
                  >
                    <option value="" disabled>
                      Elegir rol...
                    </option>
                    {roles
                      ?.filter((r) => !user.roles.includes(r.name))
                      .map((role) => (
                        <option key={role.id} value={role.name}>
                          {role.name}
                        </option>
                      ))}
                  </select>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {data && data.totalPages > 1 && (
        <div className="mt-4 flex items-center justify-center gap-3">
          <button
            className="btn-secondary"
            disabled={page <= 1}
            onClick={() => setPage((p) => p - 1)}
          >
            Anterior
          </button>
          <span className="text-sm text-ink-500">
            Página {data.page} de {data.totalPages}
          </span>
          <button
            className="btn-secondary"
            disabled={page >= data.totalPages}
            onClick={() => setPage((p) => p + 1)}
          >
            Siguiente
          </button>
        </div>
      )}
    </div>
  );
}
