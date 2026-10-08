import { useAuth } from '@/application/hooks/auth-context';
import { useState } from 'react';
import { Link, NavLink } from 'react-router-dom';

const NAV_LINKS = [
  { to: '/', label: 'Inicio' },
  { to: '/catalogo', label: 'Catálogo' },
  { to: '/acerca', label: 'La plataforma' },
  { to: '/proyecto-final', label: 'Presentación' },
];

function navLinkClass({ isActive }: { isActive: boolean }): string {
  return `relative py-1 text-sm font-semibold uppercase tracking-wide transition-colors after:absolute after:-bottom-1 after:left-0 after:h-0.5 after:w-full after:origin-left after:scale-x-0 after:bg-brand-500 after:transition-transform after:content-[''] hover:after:scale-x-100 ${
    isActive ? 'text-brand-600 after:scale-x-100' : 'text-navy-700 hover:text-brand-600'
  }`;
}

export function Header() {
  const { user, logout } = useAuth();
  const [menuOpen, setMenuOpen] = useState(false);

  return (
    <header className="sticky top-0 z-40 bg-white shadow-sm">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-4 sm:px-6 lg:px-8">
        <Link to="/" className="flex items-center gap-2.5">
          <span className="flex h-9 w-9 items-center justify-center rounded-lg bg-brand-500 text-white">
            <svg viewBox="0 0 24 24" className="h-5 w-5" fill="none" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M4 6h16M4 12h10M4 18h7" />
              <path strokeLinecap="round" strokeLinejoin="round" d="M17 14l3 3-3 3" />
            </svg>
          </span>
          <span className="text-lg font-bold tracking-tight text-navy-900">
            Vibe<span className="text-brand-600">Coding</span>
          </span>
        </Link>

        <nav className="hidden items-center gap-8 md:flex">
          {NAV_LINKS.map((link) => (
            <NavLink key={link.to} to={link.to} className={navLinkClass} end={link.to === '/'}>
              {link.label}
            </NavLink>
          ))}
        </nav>

        <div className="hidden items-center gap-4 md:flex">
          {user ? (
            <>
              {user.roles.some((r) => r !== 'STUDENT') && (
                <Link
                  to="/admin"
                  className="text-sm font-semibold uppercase tracking-wide text-navy-700 hover:text-brand-600"
                >
                  Administración
                </Link>
              )}
              <Link
                to="/perfil"
                className="text-sm font-semibold text-navy-700 hover:text-brand-600"
              >
                {user.fullName}
              </Link>
              <button
                onClick={logout}
                className="inline-flex items-center gap-2 rounded-md bg-brand-500 px-5 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-brand-600"
              >
                Salir
              </button>
            </>
          ) : (
            <Link
              to="/login"
              className="inline-flex items-center gap-2 rounded-md bg-brand-500 px-5 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-brand-600"
            >
              Ingresar
              <svg viewBox="0 0 24 24" className="h-4 w-4" fill="none" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M5 12h14M13 6l6 6-6 6" />
              </svg>
            </Link>
          )}
        </div>

        <button
          className="rounded-md p-2 text-navy-700 md:hidden"
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
              <button
                onClick={logout}
                className="rounded-md bg-brand-500 px-5 py-2.5 text-sm font-semibold text-white"
              >
                Salir
              </button>
            ) : (
              <Link
                to="/login"
                className="rounded-md bg-brand-500 px-5 py-2.5 text-center text-sm font-semibold text-white"
              >
                Ingresar
              </Link>
            )}
          </nav>
        </div>
      )}
    </header>
  );
}
