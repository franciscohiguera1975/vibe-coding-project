import { useAuth } from '@/application/hooks/auth-context';
import type { ReactNode } from 'react';
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

  if (isLoading) {
    return (
      <div className="flex min-h-[50vh] items-center justify-center text-sm text-ink-500">
        Cargando sesión...
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/login" state={{ from: location.pathname }} replace />;
  }

  if (requirePermission && !hasPermission(requirePermission)) {
    return (
      <div className="mx-auto max-w-xl px-4 py-16 text-center">
        <h1 className="text-xl font-semibold text-ink-900">Acceso restringido</h1>
        <p className="mt-2 text-sm text-ink-500">
          No tiene el permiso necesario ({requirePermission}) para ver esta sección.
        </p>
      </div>
    );
  }

  return <>{children}</>;
}
