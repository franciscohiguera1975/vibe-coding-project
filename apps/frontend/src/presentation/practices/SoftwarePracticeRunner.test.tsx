import type { PracticeDetail } from '@/domain/entities/practice';
import { SoftwarePracticeRunner } from '@/presentation/practices/SoftwarePracticeRunner';
import { fireEvent, render, screen } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';

function buildPractice(overrides: Partial<PracticeDetail> = {}): PracticeDetail {
  return {
    id: '1',
    slug: 'software-01-simulacion-mru',
    title: 'Simulación de MRU',
    description: '',
    type: 'software',
    difficulty: 'beginner',
    estimatedTimeMinutes: 45,
    technologies: [],
    status: 'published',
    categoryId: null,
    objectives: [],
    instructions: '',
    content: {
      model: {
        variables: {
          speed_kmh: { label: 'Velocidad', unit: 'km/h', min: 0, max: 100 },
          time_h: { label: 'Tiempo', unit: 'h', min: 0, max: 3 },
        },
        assumptions: ['velocidad constante'],
      },
      worked_examples: [{ speed_kmh: 60, time_h: 2, distance_km: 120 }],
    },
    evaluation: {
      checks: [{ field: 'distance_km_case1', expected: 120, tolerance: 0.01 }],
    },
    aiConfiguration: {},
    embeddingConfiguration: {},
    metadata: {},
    ...overrides,
  };
}

describe('SoftwarePracticeRunner', () => {
  it('shows the interactive simulator when content.model.variables has speed_kmh and time_h', () => {
    render(
      <SoftwarePracticeRunner
        practice={buildPractice()}
        onSubmit={vi.fn()}
        isSubmitting={false}
      />,
    );
    expect(screen.getByText('Simulación interactiva')).toBeInTheDocument();
    expect(screen.queryByText('Autoevaluación contra los criterios')).not.toBeInTheDocument();
  });

  it('falls back to the manual-check form when the model variables are not recognized', () => {
    // Regresion: un bug previo en el transform camelCase/snake_case del cliente
    // HTTP convertia "speed_kmh" en "speedKmh" dentro de `content`, lo que hacia
    // que este chequeo fallara silenciosamente y mostrara el fallback manual.
    render(
      <SoftwarePracticeRunner
        practice={buildPractice({
          content: { model: { variables: { speedKmh: {}, timeH: {} } } },
          evaluation: { checks: [{ field: 'distance_km_case1', expected: 120 }] },
        })}
        onSubmit={vi.fn()}
        isSubmitting={false}
      />,
    );
    expect(screen.queryByText('Simulación interactiva')).not.toBeInTheDocument();
    expect(screen.getByText('Autoevaluación contra los criterios')).toBeInTheDocument();
  });

  it('computes the predicted distance and submits auto-filled worked-example values', async () => {
    const onSubmit = vi.fn().mockResolvedValue(undefined);
    render(
      <SoftwarePracticeRunner practice={buildPractice()} onSubmit={onSubmit} isSubmitting={false} />,
    );

    fireEvent.change(screen.getByPlaceholderText('Su predicción en km'), {
      target: { value: '120' },
    });
    fireEvent.click(screen.getByRole('button', { name: 'Calcular' }));

    expect(screen.getByText(/Resultado:/)).toBeInTheDocument();
    expect(screen.getByText(/coincide con el modelo/)).toBeInTheDocument();

    fireEvent.click(screen.getByRole('button', { name: 'Enviar resultado' }));
    expect(onSubmit).toHaveBeenCalledWith({ distance_km_case1: 120 });
  });
});
