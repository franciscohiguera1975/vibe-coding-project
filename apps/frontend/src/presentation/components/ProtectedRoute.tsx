import { useAuth } from '@/application/hooks/auth-context';
import type { ReactNode } from 'react';
import { useTranslation } from 'react-i18next';
import { Navigate, useLocation } from 'react-router-dom';

export function ProtectedRoute({
  children,
  requirePermission,
}: {
  children: ReactNode;
  requirePermission?: string;
}) {
  const { user, isLoading, hasPermission } = useAuth();
  const location = useLocation();
  const { t } = useTranslation();

  if (isLoading) {
    return (
      <div className="flex min-h-[50vh] items-center justify-center text-sm text-ink-500">
        {t('protectedRoute.loadingSession')}
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/login" state={{ from: location.pathname }} replace />;
  }

  if (requirePermission && !hasPermission(requirePermission)) {
    return (
      <div className="mx-auto max-w-xl px-4 py-16 text-center">
        <h1 className="text-xl font-semibold text-ink-900">
          {t('protectedRoute.restricted.title')}
        </h1>
        <p className="mt-2 text-sm text-ink-500">
          {t('protectedRoute.restricted.description', { permission: requirePermission })}
        </p>
      </div>
    );
  }

  return <>{children}</>;
}
