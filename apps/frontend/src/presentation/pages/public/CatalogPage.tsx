import { usePractices } from '@/application/hooks/use-practices';
import type { PracticeFilters } from '@/domain/entities/practice';
import { PracticeCard } from '@/presentation/components/PracticeCard';
import { PageHeader } from '@/presentation/components/PageHeader';
import { useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useSearchParams } from 'react-router-dom';

export function CatalogPage() {
  const { t } = useTranslation();
  const [searchParams] = useSearchParams();
  const [type, setType] = useState(() => searchParams.get('type') ?? '');
  const [difficulty, setDifficulty] = useState('');
  const [search, setSearch] = useState('');
  const [page, setPage] = useState(1);

  const TYPE_OPTIONS = [
    { value: '', label: t('catalogPage.filters.typeAll') },
    { value: 'software', label: t('catalogPage.filters.typeSoftware') },
    { value: 'image', label: t('catalogPage.filters.typeImage') },
  ];

  const DIFFICULTY_OPTIONS = [
    { value: '', label: t('catalogPage.filters.difficultyAll') },
    { value: 'beginner', label: t('catalogPage.filters.difficultyBeginner') },
    { value: 'intermediate', label: t('catalogPage.filters.difficultyIntermediate') },
    { value: 'advanced', label: t('catalogPage.filters.difficultyAdvanced') },
  ];

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
    <div>
      <PageHeader
        title={t('catalogPage.pageTitle')}
        breadcrumbs={[
          { label: t('catalogPage.breadcrumbs.home'), to: '/' },
          { label: t('catalogPage.breadcrumbs.catalog') },
        ]}
      />

      <div className="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
        <p className="max-w-2xl text-ink-500">{t('catalogPage.filters.description')}</p>

        <div className="mt-6 flex flex-wrap gap-3">
          <input
            className="input max-w-xs"
            placeholder={t('catalogPage.filters.searchPlaceholder')}
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
          {isLoading && (
            <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
              {[1, 2, 3].map((i) => (
                <div key={i} className="card h-72 animate-pulse overflow-hidden">
                  <div className="h-40 bg-ink-100" />
                  <div className="space-y-2 p-5">
                    <div className="h-4 w-3/4 rounded bg-ink-100" />
                    <div className="h-3 w-full rounded bg-ink-100" />
                    <div className="h-3 w-5/6 rounded bg-ink-100" />
                  </div>
                </div>
              ))}
            </div>
          )}
          {isError && <p className="text-sm text-rose-600">{t('catalogPage.errors.loadFailed')}</p>}
          {data && data.items.length === 0 && (
            <p className="text-sm text-ink-500">{t('catalogPage.empty')}</p>
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
                {t('catalogPage.pagination.previous')}
              </button>
              <span className="text-sm text-ink-500">
                {t('catalogPage.pagination.pageOf', { page: data.page, totalPages: data.totalPages })}
              </span>
              <button
                className="btn-secondary"
                disabled={page >= data.totalPages}
                onClick={() => setPage((p) => p + 1)}
              >
                {t('catalogPage.pagination.next')}
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
