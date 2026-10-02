import { usePractices } from '@/application/hooks/use-practices';
import type { PracticeFilters } from '@/domain/entities/practice';
import { PracticeCard } from '@/presentation/components/PracticeCard';
import { useMemo, useState } from 'react';

const TYPE_OPTIONS = [
  { value: '', label: 'Todos los tipos' },
  { value: 'software', label: 'Desarrollo de software' },
  { value: 'image', label: 'Manejo de imágenes' },
];

const DIFFICULTY_OPTIONS = [
  { value: '', label: 'Todos los niveles' },
  { value: 'beginner', label: 'Principiante' },
  { value: 'intermediate', label: 'Intermedio' },
  { value: 'advanced', label: 'Avanzado' },
];

export function CatalogPage() {
  const [type, setType] = useState('');
  const [difficulty, setDifficulty] = useState('');
  const [search, setSearch] = useState('');
  const [page, setPage] = useState(1);

  const filters: PracticeFilters = useMemo(
    () => ({
      status: 'published',
      type: type || undefined,
      difficulty: (difficulty || undefined) as PracticeFilters['difficulty'],
      search: search || undefined,
    }),
    [type, difficulty, search],
  );

  const { data, isLoading, isError } = usePractices(filters, page);

  return (
    <div className="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
      <div className="max-w-2xl">
        <h1 className="text-3xl font-bold text-ink-900">Catálogo de prácticas</h1>
        <p className="mt-2 text-ink-500">
          Filtre por tipo, nivel o palabra clave para encontrar la práctica adecuada.
        </p>
      </div>

      <div className="mt-6 flex flex-wrap gap-3">
        <input
          className="input max-w-xs"
          placeholder="Buscar por título..."
          value={search}
          onChange={(e) => {
            setPage(1);
            setSearch(e.target.value);
          }}
        />
        <select
          className="input max-w-xs"
          value={type}
          onChange={(e) => {
            setPage(1);
            setType(e.target.value);
          }}
        >
          {TYPE_OPTIONS.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>
        <select
          className="input max-w-xs"
          value={difficulty}
          onChange={(e) => {
            setPage(1);
            setDifficulty(e.target.value);
          }}
        >
          {DIFFICULTY_OPTIONS.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>
      </div>

      <div className="mt-8">
        {isLoading && <p className="text-sm text-ink-500">Cargando prácticas...</p>}
        {isError && <p className="text-sm text-rose-600">No se pudo cargar el catálogo.</p>}
        {data && data.items.length === 0 && (
          <p className="text-sm text-ink-500">No hay prácticas que coincidan con los filtros.</p>
        )}

        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {data?.items.map((practice) => (
            <PracticeCard key={practice.id} practice={practice} />
          ))}
        </div>

        {data && data.totalPages > 1 && (
          <div className="mt-8 flex items-center justify-center gap-3">
            <button
              className="btn-secondary"
              disabled={page <= 1}
              onClick={() => setPage((p) => Math.max(1, p - 1))}
            >
              Anterior
            </button>
            <span className="text-sm text-ink-500">
              Página {data.page} de {data.totalPages}
            </span>
            <button
              className="btn-secondary"
              disabled={page >= data.totalPages}
              onClick={() => setPage((p) => p + 1)}
            >
              Siguiente
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
