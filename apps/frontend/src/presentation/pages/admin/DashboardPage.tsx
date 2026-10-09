import { useAuth } from '@/application/hooks/auth-context';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';

export function DashboardPage() {
  const { user } = useAuth();
  const { t } = useTranslation();

  const CARDS = [
    {
      to: '/admin/practicas',
      title: t('dashboardPage.cards.practices.title'),
      description: t('dashboardPage.cards.practices.description'),
    },
    {
      to: '/admin/categorias',
      title: t('dashboardPage.cards.categories.title'),
      description: t('dashboardPage.cards.categories.description'),
    },
    {
      to: '/admin/usuarios',
      title: t('dashboardPage.cards.users.title'),
      description: t('dashboardPage.cards.users.description'),
    },
    {
      to: '/admin/roles',
      title: t('dashboardPage.cards.roles.title'),
      description: t('dashboardPage.cards.roles.description'),
    },
    {
      to: '/admin/configuraciones',
      title: t('dashboardPage.cards.configurations.title'),
      description: t('dashboardPage.cards.configurations.description'),
    },
    {
      to: '/admin/auditoria',
      title: t('dashboardPage.cards.audit.title'),
      description: t('dashboardPage.cards.audit.description'),
    },
  ];

  return (
    <div>
      <h1 className="text-2xl font-semibold text-ink-900">{t('dashboardPage.title')}</h1>
      <p className="mt-1 text-sm text-ink-500">
        {t('dashboardPage.welcome', { name: user?.fullName })}
      </p>

      <div className="mt-8 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {CARDS.map((card) => (
          <Link key={card.to} to={card.to} className="card p-5 transition-shadow hover:shadow-md">
            <h2 className="font-semibold text-ink-900">{card.title}</h2>
            <p className="mt-1 text-sm text-ink-500">{card.description}</p>
          </Link>
        ))}
      </div>
    </div>
  );
}
