import { useAuth } from '@/application/hooks/auth-context';
import { useState } from 'react';
import { Link, NavLink } from 'react-router-dom';

const NAV_LINKS = [
  { to: '/', label: 'Inicio' },
  { to: '/catalogo', label: 'Catálogo' },
  { to: '/acerca', label: 'La plataforma' },
];

function navLinkClass({ isActive }: { isActive: boolean }): string {
  return `text-sm font-medium transition-colors ${
    isActive ? 'text-brand-700' : 'text-ink-600 hover:text-brand-600'
  }`;
}

export function Header() {
  const { user, logout } = useAuth();
  const [menuOpen, setMenuOpen] = useState(false);

  return (
    <header className="sticky top-0 z-40 border-b border-ink-100 bg-white shadow-sm">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-3 sm:px-6 lg:px-8">
        <Link to="/" className="flex items-center gap-2">
          <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-brand-600 text-sm font-bold text-white">
            VC
          </span>
          <span className="text-base font-semibold text-ink-900">Vibe Coding Platform</span>
        </Link>

        <nav className="hidden items-center gap-6 md:flex">
          {NAV_LINKS.map((link) => (
            <NavLink key={link.to} to={link.to} className={navLinkClass} end={link.to === '/'}>
              {link.label}
            </NavLink>
          ))}
        </nav>

        <div className="hidden items-center gap-3 md:flex">
          {user ? (
            <>
              {user.roles.some((r) => r !== 'STUDENT') && (
                <Link to="/admin" className="btn-secondary">
                  Administración
                </Link>
              )}
              <Link to="/perfil" className="text-sm font-medium text-ink-700 hover:text-brand-600">
                {user.fullName}
              </Link>
              <button onClick={logout} className="btn-secondary">
                Salir
              </button>
            </>
          ) : (
            <Link to="/login" className="btn-primary">
              Ingresar
            </Link>
          )}
        </div>

        <button
          className="rounded-md p-2 text-ink-600 md:hidden"
          onClick={() => setMenuOpen((v) => !v)}
          aria-label="Abrir menú"
        >
          <svg
            viewBox="0 0 24 24"
            className="h-6 w-6"
            fill="none"
            stroke="currentColor"
            strokeWidth={2}
          >
            <path strokeLinecap="round" strokeLinejoin="round" d="M4 6h16M4 12h16M4 18h16" />
          </svg>
        </button>
      </div>

      {menuOpen && (
        <div className="border-t border-ink-100 px-4 py-3 md:hidden">
          <nav className="flex flex-col gap-3">
            {NAV_LINKS.map((link) => (
              <NavLink key={link.to} to={link.to} className={navLinkClass} end={link.to === '/'}>
                {link.label}
              </NavLink>
            ))}
            {user ? (
              <button onClick={logout} className="btn-secondary w-full">
                Salir
              </button>
            ) : (
              <Link to="/login" className="btn-primary w-full">
                Ingresar
              </Link>
            )}
          </nav>
        </div>
      )}
    </header>
  );
}
