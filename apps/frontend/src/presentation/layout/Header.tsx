import { useAuth } from '@/application/hooks/auth-context';
import { LanguageSwitcher } from '@/presentation/components/LanguageSwitcher';
import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Link, NavLink } from 'react-router-dom';

function navLinkClass({ isActive }: { isActive: boolean }): string {
  return `relative py-1 text-sm font-semibold uppercase tracking-wide transition-colors after:absolute after:-bottom-1 after:left-0 after:h-0.5 after:w-full after:origin-left after:scale-x-0 after:bg-brand-500 after:transition-transform after:content-[''] hover:after:scale-x-100 ${
    isActive ? 'text-brand-600 after:scale-x-100' : 'text-navy-700 hover:text-brand-600'
  }`;
}

export function Header() {
  const { user, logout } = useAuth();
  const { t } = useTranslation();
  const [menuOpen, setMenuOpen] = useState(false);
  const [ragMenuOpen, setRagMenuOpen] = useState(false);

  const navLinks = [
    { to: '/', label: t('header.nav.home') },
    { to: '/catalogo', label: t('header.nav.catalog') },
    { to: '/acerca', label: t('header.nav.about') },
    { to: '/proyecto-final', label: t('header.nav.presentation') },
  ];

  const ragLinks = [
    { to: '/validacion-silabos', label: t('header.nav.syllabusValidation') },
    { to: '/evaluacion-rag', label: t('header.nav.ragEvaluation') },
  ];

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
          {navLinks.map((link) => (
            <NavLink key={link.to} to={link.to} className={navLinkClass} end={link.to === '/'}>
              {link.label}
            </NavLink>
          ))}
          <div
            className="relative"
            onMouseEnter={() => setRagMenuOpen(true)}
            onMouseLeave={() => setRagMenuOpen(false)}
          >
            <button
              type="button"
              className="relative py-1 text-sm font-semibold uppercase tracking-wide text-navy-700 transition-colors hover:text-brand-600"
              onClick={() => setRagMenuOpen((v) => !v)}
              aria-expanded={ragMenuOpen}
            >
              {t('header.nav.rag')}
            </button>
            {ragMenuOpen && (
              <div className="absolute left-0 top-full z-50 mt-2 w-56 rounded-md border border-ink-100 bg-white py-2 shadow-lg">
                {ragLinks.map((link) => (
                  <NavLink
                    key={link.to}
                    to={link.to}
                    className="block px-4 py-2 text-sm font-medium text-navy-700 hover:bg-brand-50 hover:text-brand-600"
                    onClick={() => setRagMenuOpen(false)}
                  >
                    {link.label}
                  </NavLink>
                ))}
              </div>
            )}
          </div>
        </nav>

        <div className="hidden items-center gap-4 md:flex">
          <LanguageSwitcher />
          {user ? (
            <>
              {user.roles.some((r) => r !== 'STUDENT') && (
                <Link
                  to="/admin"
                  className="text-sm font-semibold uppercase tracking-wide text-navy-700 hover:text-brand-600"
                >
                  {t('header.admin')}
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
                {t('header.logout')}
              </button>
            </>
          ) : (
            <Link
              to="/login"
              className="inline-flex items-center gap-2 rounded-md bg-brand-500 px-5 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-brand-600"
            >
              {t('header.login')}
              <svg viewBox="0 0 24 24" className="h-4 w-4" fill="none" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M5 12h14M13 6l6 6-6 6" />
              </svg>
            </Link>
          )}
        </div>

        <button
          className="rounded-md p-2 text-navy-700 md:hidden"
          onClick={() => setMenuOpen((v) => !v)}
          aria-label={t('header.openMenu')}
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
            {navLinks.map((link) => (
              <NavLink key={link.to} to={link.to} className={navLinkClass} end={link.to === '/'}>
                {link.label}
              </NavLink>
            ))}
            <span className="text-xs font-semibold uppercase tracking-wide text-ink-400">
              {t('header.nav.rag')}
            </span>
            {ragLinks.map((link) => (
              <NavLink key={link.to} to={link.to} className={navLinkClass}>
                {link.label}
              </NavLink>
            ))}
            <LanguageSwitcher />
            {user ? (
              <button
                onClick={logout}
                className="rounded-md bg-brand-500 px-5 py-2.5 text-sm font-semibold text-white"
              >
                {t('header.logout')}
              </button>
            ) : (
              <Link
                to="/login"
                className="rounded-md bg-brand-500 px-5 py-2.5 text-center text-sm font-semibold text-white"
              >
                {t('header.login')}
              </Link>
            )}
          </nav>
        </div>
      )}
    </header>
  );
}
