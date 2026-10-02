import { PublicLayout } from '@/presentation/layout/PublicLayout';
import { AboutPage } from '@/presentation/pages/public/AboutPage';
import { CatalogPage } from '@/presentation/pages/public/CatalogPage';
import { HomePage } from '@/presentation/pages/public/HomePage';
import { NotFoundPage } from '@/presentation/pages/public/NotFoundPage';
import { LoginPage } from '@/presentation/pages/auth/LoginPage';
import { Route, Routes } from 'react-router-dom';

export default function App() {
  return (
    <Routes>
      <Route element={<PublicLayout />}>
        <Route index element={<HomePage />} />
        <Route path="catalogo" element={<CatalogPage />} />
        <Route path="acerca" element={<AboutPage />} />
        <Route path="login" element={<LoginPage />} />
        <Route path="*" element={<NotFoundPage />} />
      </Route>
    </Routes>
  );
}
