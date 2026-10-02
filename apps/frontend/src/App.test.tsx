import { AuthProvider } from '@/application/hooks/auth-context';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { describe, expect, it, vi } from 'vitest';
import App from './App';

vi.mock('@/infrastructure/container', () => ({
  authService: { me: vi.fn().mockRejectedValue(new Error('no token')) },
  practiceService: {
    list: vi.fn().mockResolvedValue({ items: [], total: 0, page: 1, pageSize: 12, totalPages: 0 }),
  },
  userService: {},
  roleService: {},
  tokenStorage: {
    getAccessToken: () => null,
    getRefreshToken: () => null,
    setTokens: vi.fn(),
    clear: vi.fn(),
  },
}));

function renderApp(initialPath = '/') {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <MemoryRouter initialEntries={[initialPath]}>
          <App />
        </MemoryRouter>
      </AuthProvider>
    </QueryClientProvider>,
  );
}

describe('App routing', () => {
  it('renders the home page hero by default', async () => {
    renderApp('/');
    expect(await screen.findByText(/Aprenda a construir software/i)).toBeInTheDocument();
  });

  it('renders the catalog page', async () => {
    renderApp('/catalogo');
    expect(
      await screen.findByRole('heading', { name: /Catálogo de prácticas/i }),
    ).toBeInTheDocument();
  });

  it('renders a 404 page for unknown routes', async () => {
    renderApp('/ruta-inexistente');
    expect(await screen.findByText(/Página no encontrada/i)).toBeInTheDocument();
  });
});
