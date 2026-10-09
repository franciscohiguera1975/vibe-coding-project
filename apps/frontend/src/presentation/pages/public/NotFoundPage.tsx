import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';

export function NotFoundPage() {
  const { t } = useTranslation();

  return (
    <div className="mx-auto flex min-h-[60vh] max-w-xl flex-col items-center justify-center px-4 text-center">
      <p className="text-sm font-semibold text-brand-600">404</p>
      <h1 className="mt-2 text-2xl font-semibold text-ink-900">{t('notFoundPage.title')}</h1>
      <p className="mt-2 text-sm text-ink-500">{t('notFoundPage.description')}</p>
      <Link to="/" className="btn-primary mt-6">
        {t('notFoundPage.backHome')}
      </Link>
    </div>
  );
}
