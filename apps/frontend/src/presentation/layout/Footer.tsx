import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';

function ScrollToTopButton() {
  const { t } = useTranslation();
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    function onScroll() {
      setVisible(window.scrollY > 400);
    }
    window.addEventListener('scroll', onScroll, { passive: true });
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  if (!visible) return null;

  return (
    <button
      type="button"
      aria-label={t('footer.scrollToTop')}
      onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}
      className="fixed bottom-6 right-6 z-30 flex h-11 w-11 items-center justify-center rounded-md bg-brand-500 text-white shadow-lg transition-colors hover:bg-brand-600"
    >
      <svg viewBox="0 0 24 24" className="h-5 w-5" fill="none" stroke="currentColor" strokeWidth={2}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M12 19V5M6 11l6-6 6 6" />
      </svg>
    </button>
  );
}

export function Footer() {
  const { t } = useTranslation();

  return (
    <footer className="bg-navy-900 text-ink-200">
      <div className="mx-auto max-w-7xl px-4 py-14 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 gap-10 sm:grid-cols-2 lg:grid-cols-4">
          <div>
            <span className="text-lg font-bold tracking-tight text-white">
              Vibe<span className="text-brand-400">Coding</span>
            </span>
            <p className="mt-3 max-w-xs text-sm text-ink-300">{t('footer.description')}</p>
          </div>
          <div>
            <h3 className="text-sm font-semibold uppercase tracking-wide text-white">
              {t('footer.explore.heading')}
            </h3>
            <ul className="mt-4 space-y-2.5 text-sm text-ink-300">
              <li>
                <Link to="/catalogo" className="hover:text-brand-300">
                  {t('footer.explore.catalog')}
                </Link>
              </li>
              <li>
                <Link to="/catalogo?type=software" className="hover:text-brand-300">
                  {t('footer.explore.software')}
                </Link>
              </li>
              <li>
                <Link to="/catalogo?type=image" className="hover:text-brand-300">
                  {t('footer.explore.image')}
                </Link>
              </li>
              <li>
                <Link to="/acerca" className="hover:text-brand-300">
                  {t('footer.explore.about')}
                </Link>
              </li>
            </ul>
          </div>
          <div>
            <h3 className="text-sm font-semibold uppercase tracking-wide text-white">
              {t('footer.integration.heading')}
            </h3>
            <ul className="mt-4 space-y-2.5 text-sm text-ink-300">
              <li>{t('footer.integration.embed')}</li>
              <li>{t('footer.integration.api')}</li>
              <li>{t('footer.integration.tutor')}</li>
            </ul>
          </div>
          <div>
            <h3 className="text-sm font-semibold uppercase tracking-wide text-white">
              {t('footer.access.heading')}
            </h3>
            <ul className="mt-4 space-y-2.5 text-sm text-ink-300">
              <li>
                <Link to="/login" className="hover:text-brand-300">
                  {t('footer.access.login')}
                </Link>
              </li>
              <li>
                <Link to="/catalogo" className="hover:text-brand-300">
                  {t('footer.access.viewPractices')}
                </Link>
              </li>
            </ul>
          </div>
        </div>
        <div className="mt-10 flex flex-col gap-3 border-t border-white/10 pt-6 text-xs text-ink-400 sm:flex-row sm:items-center sm:justify-between">
          <p>{t('footer.copyright', { year: new Date().getFullYear() })}</p>
          <p>{t('footer.tagline')}</p>
        </div>
      </div>
      <ScrollToTopButton />
    </footer>
  );
}
