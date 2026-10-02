import { useAuth } from '@/application/hooks/auth-context';
import { NavLink, Outlet, Link } from 'react-router-dom';

const NAV_ITEMS = [
  { to: '/admin', label: 'Dashboard', end: true },
  { to: '/admin/practicas', label: 'Prácticas' },
  { to: '/admin/categorias', label: 'Categorías' },
  { to: '/admin/usuarios', label: 'Usuarios' },
  { to: '/admin/roles', label: 'Roles y permisos' },
  { to: '/admin/configuraciones', label: 'Configuraciones' },
  { to: '/admin/auditoria', label: 'Auditoría' },
];

function navLinkClass({ isActive }: { isActive: boolean }): string {
  return `block rounded-lg px-3 py-2 text-sm font-medium transition-colors ${
    isActive ? 'bg-brand-50 text-brand-700' : 'text-ink-600 hover:bg-ink-50'
  }`;
}

export function AdminLayout() {
  const { user, logout } = useAuth();

  return (
    <div className="flex min-h-screen bg-ink-50">
      <aside className="hidden w-64 shrink-0 border-r border-ink-100 bg-white px-4 py-6 md:block">
        <Link to="/" className="flex items-center gap-2 px-2">
          <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-brand-600 text-sm font-bold text-white">
            VC
          </span>
          <span className="text-sm font-semibold text-ink-900">Administración</span>
        </Link>
        <nav className="mt-8 space-y-1">
          {NAV_ITEMS.map((item) => (
            <NavLink key={item.to} to={item.to} end={item.end} className={navLinkClass}>
              {item.label}
            </NavLink>
          ))}
        </nav>
        <div className="mt-8 border-t border-ink-100 pt-4">
          <p className="truncate px-2 text-xs text-ink-400">{user?.email}</p>
          <button onClick={logout} className="btn-secondary mt-2 w-full">
            Salir
          </button>
        </div>
      </aside>
      <main className="flex-1 px-4 py-8 sm:px-8">
        <Outlet />
      </main>
    </div>
  );
}
