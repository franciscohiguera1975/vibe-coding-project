import type { PracticeDetail } from '@/domain/entities/practice';
import { ImagePracticeRunner } from '@/presentation/practices/ImagePracticeRunner';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { fireEvent, render, screen } from '@testing-library/react';
import type { ReactElement } from 'react';
import { describe, expect, it, vi } from 'vitest';

vi.mock('@/infrastructure/container', () => ({
  imageService: { analyze: vi.fn() },
}));

function buildPractice(overrides: Partial<PracticeDetail> = {}): PracticeDetail {
  return {
    id: '1',
    slug: 'image-01-conteo-circulos',
    title: 'Prototipo de conteo de círculos de papel',
    description: '',
    type: 'image',
    difficulty: 'beginner',
    estimatedTimeMinutes: 50,
    technologies: [],
    status: 'published',
    categoryId: null,
    objectives: [],
    instructions: '',
    content: {
      counting_rule: { counts: 'un círculo cuyo centro es visible', excludes: ['reflejos'] },
      required_output: ['tabla de error por condición'],
    },
    evaluation: { strategy: 'count_comparison', reference: { 'img-1': 3, 'img-2': 5 } },
    aiConfiguration: {},
    embeddingConfiguration: {},
    metadata: {},
    ...overrides,
  };
}

function renderWithQueryClient(ui: ReactElement) {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(<QueryClientProvider client={queryClient}>{ui}</QueryClientProvider>);
}

describe('ImagePracticeRunner', () => {
  it('renders a file upload slot per reference image for the count_comparison strategy', () => {
    renderWithQueryClient(
      <ImagePracticeRunner practice={buildPractice()} onSubmit={vi.fn()} isSubmitting={false} />,
    );

    expect(screen.getByText('img-1')).toBeInTheDocument();
    expect(screen.getByText('img-2')).toBeInTheDocument();
    expect(screen.getByText(/un círculo cuyo centro es visible/)).toBeInTheDocument();
  });

  it('renders a text report form for the manual strategy', () => {
    const onSubmit = vi.fn().mockResolvedValue(undefined);
    renderWithQueryClient(
      <ImagePracticeRunner
        practice={buildPractice({ evaluation: { strategy: 'manual' } })}
        onSubmit={onSubmit}
        isSubmitting={false}
      />,
    );

    expect(screen.queryByText('img-1')).not.toBeInTheDocument();
    const submitButton = screen.getByRole('button', { name: /Enviar informe/ });
    expect(submitButton).toBeDisabled();

    fireEvent.change(screen.getByPlaceholderText(/Describa su diagnóstico/), {
      target: { value: 'Iluminación pobre en 2 imágenes.' },
    });
    expect(submitButton).not.toBeDisabled();

    fireEvent.click(submitButton);
    expect(onSubmit).toHaveBeenCalledWith({ report: 'Iluminación pobre en 2 imágenes.' });
  });
});
