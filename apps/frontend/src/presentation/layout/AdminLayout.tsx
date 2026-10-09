import { useAuth } from '@/application/hooks/auth-context';
import { useTranslation } from 'react-i18next';
import { NavLink, Outlet, Link } from 'react-router-dom';

function navLinkClass({ isActive }: { isActive: boolean }): string {
  return `block rounded-lg border-l-2 px-4 py-2.5 text-sm font-medium transition-colors ${
    isActive
      ? 'border-brand-400 bg-white/10 text-white'
      : 'border-transparent text-ink-300 hover:bg-white/5 hover:text-white'
  }`;
}

export function AdminLayout() {
  const { user, logout } = useAuth();
  const { t } = useTranslation();

  const NAV_ITEMS = [
    { to: '/admin', label: t('adminLayout.nav.dashboard'), end: true },
    { to: '/admin/practicas', label: t('adminLayout.nav.practices') },
    { to: '/admin/categorias', label: t('adminLayout.nav.categories') },
    { to: '/admin/usuarios', label: t('adminLayout.nav.users') },
    { to: '/admin/roles', label: t('adminLayout.nav.roles') },
    { to: '/admin/configuraciones', label: t('adminLayout.nav.configurations') },
    { to: '/admin/auditoria', label: t('adminLayout.nav.audit') },
  ];

  return (
    <div className="flex min-h-screen bg-ink-50">
      {/* fixed (no sticky): el sidebar completo, incluido el bloque de
          usuario/Salir anclado abajo con mt-auto, debe quedar fuera del flujo
          de scroll de <main> sin importar cuanto crezca el contenido admin. */}
      <aside className="fixed inset-y-0 left-0 hidden w-64 flex-col bg-navy-900 px-4 py-6 md:flex">
        <Link to="/" className="flex shrink-0 items-center gap-2.5 px-2">
          <span className="flex h-9 w-9 items-center justify-center rounded-lg bg-brand-500 text-white">
            <svg viewBox="0 0 24 24" className="h-5 w-5" fill="none" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M4 6h16M4 12h10M4 18h7" />
              <path strokeLinecap="round" strokeLinejoin="round" d="M17 14l3 3-3 3" />
            </svg>
          </span>
          <span>
            <span className="block text-sm font-bold tracking-tight text-white">
              Vibe<span className="text-brand-400">Coding</span>
            </span>
            <span className="block text-xs text-ink-400">{t('adminLayout.subtitle')}</span>
          </span>
        </Link>
        <nav className="mt-8 flex-1 space-y-1 overflow-y-auto">
          {NAV_ITEMS.map((item) => (
            <NavLink key={item.to} to={item.to} end={item.end} className={navLinkClass}>
              {item.label}
            </NavLink>
          ))}
        </nav>
        <div className="mt-4 shrink-0 border-t border-white/10 pt-4">
          <p className="truncate px-2 text-xs text-ink-400">{user?.email}</p>
          <button
            onClick={logout}
            className="mt-2 w-full rounded-md bg-white/10 px-4 py-2 text-sm font-semibold text-white transition-colors hover:bg-white/20"
          >
            {t('adminLayout.logout')}
          </button>
        </div>
      </aside>
      <main className="flex-1 px-4 py-8 sm:px-8 md:ml-64">
        <Outlet />
      </main>
    </div>
  );
}
