import { useAuth } from '@/application/hooks/auth-context';
import { PageHeader } from '@/presentation/components/PageHeader';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';

export function AccountSecurityPage() {
  const { t } = useTranslation();
  const { user } = useAuth();

  if (!user) {
    return null;
  }

  return (
    <div>
      <PageHeader
        title={t('accountSecurityPage.pageTitle')}
        breadcrumbs={[
          { label: t('accountSecurityPage.breadcrumbs.home'), to: '/' },
          { label: t('accountSecurityPage.breadcrumbs.account') },
        ]}
      />

      <div className="mx-auto max-w-2xl px-4 py-12 sm:px-6 lg:px-8">
        <section className="rounded-lg border border-ink-100 bg-white p-6 shadow-sm">
          <h2 className="text-lg font-semibold text-navy-900">
            {t('accountSecurityPage.account.title')}
          </h2>
          <dl className="mt-4 space-y-4">
            <div>
              <dt className="text-xs font-semibold uppercase tracking-wide text-ink-400">
                {t('accountSecurityPage.account.fullName')}
              </dt>
              <dd className="mt-1 text-sm text-navy-700">{user.fullName}</dd>
            </div>
            <div>
              <dt className="text-xs font-semibold uppercase tracking-wide text-ink-400">
                {t('accountSecurityPage.account.email')}
              </dt>
              <dd className="mt-1 text-sm text-navy-700">{user.email}</dd>
            </div>
            <div>
              <dt className="text-xs font-semibold uppercase tracking-wide text-ink-400">
                {t('accountSecurityPage.account.roles')}
              </dt>
              <dd className="mt-1 flex flex-wrap gap-2">
                {user.roles.map((role) => (
                  <span
                    key={role}
                    className="rounded-full bg-brand-50 px-3 py-1 text-xs font-semibold text-brand-700"
                  >
                    {role}
                  </span>
                ))}
              </dd>
            </div>
          </dl>
        </section>

        <section className="mt-6 rounded-lg border border-ink-100 bg-white p-6 shadow-sm">
          <h2 className="text-lg font-semibold text-navy-900">
            {t('accountSecurityPage.security.title')}
          </h2>
          <p className="mt-2 text-sm text-ink-500">
            {t('accountSecurityPage.security.description')}
          </p>
          <Link
            to="/recuperar-contrasena"
            className="mt-4 inline-flex items-center gap-2 rounded-md bg-brand-500 px-5 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-brand-600"
          >
            {t('accountSecurityPage.security.changePasswordCta')}
          </Link>
        </section>
      </div>
    </div>
  );
}
