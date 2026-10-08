import { PublicLayout } from '@/presentation/layout/PublicLayout';
import { AdminLayout } from '@/presentation/layout/AdminLayout';
import { AboutPage } from '@/presentation/pages/public/AboutPage';
import { CatalogPage } from '@/presentation/pages/public/CatalogPage';
import { FinalProjectPage } from '@/presentation/pages/public/FinalProjectPage';
import { HomePage } from '@/presentation/pages/public/HomePage';
import { NotFoundPage } from '@/presentation/pages/public/NotFoundPage';
import { PracticeDetailPage } from '@/presentation/pages/public/PracticeDetailPage';
import { PracticeEmbedPage } from '@/presentation/pages/public/PracticeEmbedPage';
import { LoginPage } from '@/presentation/pages/auth/LoginPage';
import { DashboardPage } from '@/presentation/pages/admin/DashboardPage';
import { PracticesAdminPage } from '@/presentation/pages/admin/PracticesAdminPage';
import { CategoriesAdminPage } from '@/presentation/pages/admin/CategoriesAdminPage';
import { UsersAdminPage } from '@/presentation/pages/admin/UsersAdminPage';
import { RolesAdminPage } from '@/presentation/pages/admin/RolesAdminPage';
import { ConfigurationsAdminPage } from '@/presentation/pages/admin/ConfigurationsAdminPage';
import { AuditPage } from '@/presentation/pages/admin/AuditPage';
import { ProtectedRoute } from '@/presentation/components/ProtectedRoute';
import { Route, Routes } from 'react-router-dom';

export default function App() {
  return (
    <Routes>
      <Route path="practices/:slug/embed" element={<PracticeEmbedPage />} />

      <Route element={<PublicLayout />}>
        <Route index element={<HomePage />} />
        <Route path="catalogo" element={<CatalogPage />} />
        <Route path="catalogo/:slug" element={<PracticeDetailPage />} />
        <Route path="acerca" element={<AboutPage />} />
        <Route path="proyecto-final" element={<FinalProjectPage />} />
        <Route path="login" element={<LoginPage />} />
        <Route path="*" element={<NotFoundPage />} />
      </Route>

      <Route
        path="admin"
        element={
          <ProtectedRoute requirePermission="practice:read">
            <AdminLayout />
          </ProtectedRoute>
        }
      >
        <Route index element={<DashboardPage />} />
        <Route path="practicas" element={<PracticesAdminPage />} />
        <Route path="categorias" element={<CategoriesAdminPage />} />
        <Route path="usuarios" element={<UsersAdminPage />} />
        <Route path="roles" element={<RolesAdminPage />} />
        <Route path="configuraciones" element={<ConfigurationsAdminPage />} />
        <Route path="auditoria" element={<AuditPage />} />
      </Route>
    </Routes>
  );
}
