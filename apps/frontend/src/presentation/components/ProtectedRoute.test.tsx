import * as authContext from '@/application/hooks/auth-context';
import { ProtectedRoute } from '@/presentation/components/ProtectedRoute';
import { render, screen } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { describe, expect, it, vi } from 'vitest';

function renderProtected(requirePermission?: string) {
  return render(
    <MemoryRouter initialEntries={['/admin']}>
      <Routes>
        <Route path="/login" element={<p>Pantalla de inicio de sesión</p>} />
        <Route
          path="/admin"
          element={
            <ProtectedRoute requirePermission={requirePermission}>
              <p>Contenido protegido</p>
            </ProtectedRoute>
          }
        />
      </Routes>
    </MemoryRouter>,
  );
}

describe('ProtectedRoute', () => {
  it('redirects to /login when there is no authenticated user', () => {
    vi.spyOn(authContext, 'useAuth').mockReturnValue({
      user: null,
      isLoading: false,
      login: vi.fn(),
      logout: vi.fn(),
      hasPermission: () => false,
    });

    renderProtected();
    expect(screen.getByText('Pantalla de inicio de sesión')).toBeInTheDocument();
  });

  it('shows a loading state while the session is being resolved', () => {
    vi.spyOn(authContext, 'useAuth').mockReturnValue({
      user: null,
      isLoading: true,
      login: vi.fn(),
      logout: vi.fn(),
      hasPermission: () => false,
    });

    renderProtected();
    expect(screen.getByText(/Cargando sesión/)).toBeInTheDocument();
  });

  it('renders the restricted-access message when the user lacks the required permission', () => {
    vi.spyOn(authContext, 'useAuth').mockReturnValue({
      user: { id: '1', email: 'a@a.dev', fullName: 'A', isActive: true, roles: [], permissions: [] },
      isLoading: false,
      login: vi.fn(),
      logout: vi.fn(),
      hasPermission: () => false,
    });

    renderProtected('practice:create');
    expect(screen.getByText('Acceso restringido')).toBeInTheDocument();
  });

  it('renders the children when the user has the required permission', () => {
    vi.spyOn(authContext, 'useAuth').mockReturnValue({
      user: {
        id: '1',
        email: 'a@a.dev',
        fullName: 'A',
        isActive: true,
        roles: [],
        permissions: ['practice:read'],
      },
      isLoading: false,
      login: vi.fn(),
      logout: vi.fn(),
      hasPermission: (code) => code === 'practice:read',
    });

    renderProtected('practice:read');
    expect(screen.getByText('Contenido protegido')).toBeInTheDocument();
  });
});
