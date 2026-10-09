import {
  useCreatePractice,
  useGenerateAllNarrations,
  usePractices,
  usePublishPractice,
} from '@/application/hooks/use-practices';
import type { PracticeNarrationGenerateAllItem } from '@/domain/entities/practice';
import { Fragment, FormEvent, useState } from 'react';
import { useTranslation } from 'react-i18next';

const STATUS_COLOR: Record<string, string> = {
  draft: 'bg-ink-100 text-ink-600',
  published: 'bg-emerald-50 text-emerald-700',
  archived: 'bg-amber-50 text-amber-700',
};

export function PracticesAdminPage() {
  const { t } = useTranslation();
  const [page, setPage] = useState(1);
  const { data, isLoading } = usePractices({}, page, 20);
  const createPractice = useCreatePractice();
  const publishPractice = usePublishPractice();
  const generateAllNarrations = useGenerateAllNarrations();
  const [showForm, setShowForm] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [narrationResults, setNarrationResults] = useState<
    Record<string, PracticeNarrationGenerateAllItem[]>
  >({});
  const [narrationLoadingSlug, setNarrationLoadingSlug] = useState<string | null>(null);

  async function handleGenerateNarrations(slug: string) {
    setNarrationLoadingSlug(slug);
    try {
      const results = await generateAllNarrations.mutateAsync(slug);
      setNarrationResults((prev) => ({ ...prev, [slug]: results }));
    } finally {
      setNarrationLoadingSlug(null);
    }
  }

  const [form, setForm] = useState({
    title: '',
    type: 'software',
    instructions: '',
    content: '{}',
    evaluation: '{}',
  });

  async function handleCreate(event: FormEvent) {
    event.preventDefault();
    setError(null);
    try {
      const content = JSON.parse(form.content || '{}');
      const evaluation = JSON.parse(form.evaluation || '{}');
      await createPractice.mutateAsync({
        title: form.title,
        type: form.type,
        instructions: form.instructions,
        content,
        evaluation,
      });
      setShowForm(false);
      setForm({ title: '', type: 'software', instructions: '', content: '{}', evaluation: '{}' });
    } catch {
      setError(t('practicesAdminPage.errors.invalidJson'));
    }
  }

  return (
    <div>
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold text-ink-900">{t('practicesAdminPage.title')}</h1>
        <button className="btn-primary" onClick={() => setShowForm((v) => !v)}>
          {showForm ? t('practicesAdminPage.cancel') : t('practicesAdminPage.newPractice')}
        </button>
      </div>

      {showForm && (
        <form onSubmit={handleCreate} className="card mt-4 space-y-3 p-5">
          <div>
            <label className="label">{t('practicesAdminPage.form.titleLabel')}</label>
            <input
              required
              className="input"
              value={form.title}
              onChange={(e) => setForm((f) => ({ ...f, title: e.target.value }))}
            />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="label">{t('practicesAdminPage.form.typeLabel')}</label>
              <select
                className="input"
                value={form.type}
                onChange={(e) => setForm((f) => ({ ...f, type: e.target.value }))}
              >
                <option value="software">software</option>
                <option value="image">image</option>
              </select>
            </div>
          </div>
          <div>
            <label className="label">{t('practicesAdminPage.form.instructionsLabel')}</label>
            <textarea
              required
              className="input"
              rows={3}
              value={form.instructions}
              onChange={(e) => setForm((f) => ({ ...f, instructions: e.target.value }))}
            />
          </div>
          <div>
            <label className="label">{t('practicesAdminPage.form.contentLabel')}</label>
            <textarea
              className="input font-mono text-xs"
              rows={4}
              value={form.content}
              onChange={(e) => setForm((f) => ({ ...f, content: e.target.value }))}
            />
          </div>
          <div>
            <label className="label">{t('practicesAdminPage.form.evaluationLabel')}</label>
            <textarea
              className="input font-mono text-xs"
              rows={4}
              value={form.evaluation}
              onChange={(e) => setForm((f) => ({ ...f, evaluation: e.target.value }))}
            />
          </div>
          {error && <p className="text-sm text-rose-600">{error}</p>}
          <button type="submit" className="btn-primary" disabled={createPractice.isPending}>
            {createPractice.isPending
              ? t('practicesAdminPage.form.submitting')
              : t('practicesAdminPage.form.submit')}
          </button>
        </form>
      )}

      <div className="mt-6 overflow-x-auto">
        {isLoading && <p className="text-sm text-ink-500">{t('practicesAdminPage.loading')}</p>}
        <table className="w-full min-w-[640px] text-left text-sm">
          <thead>
            <tr className="border-b border-ink-100 text-ink-500">
              <th className="py-2">{t('practicesAdminPage.table.title')}</th>
              <th className="py-2">{t('practicesAdminPage.table.type')}</th>
              <th className="py-2">{t('practicesAdminPage.table.status')}</th>
              <th className="py-2"></th>
            </tr>
          </thead>
          <tbody>
            {data?.items.map((practice) => (
              <Fragment key={practice.id}>
                <tr className="border-b border-ink-50">
                  <td className="py-2 font-medium text-ink-900">{practice.title}</td>
                  <td className="py-2 text-ink-500">{practice.type}</td>
                  <td className="py-2">
                    <span
                      className={`badge ${STATUS_COLOR[practice.status] ?? 'bg-ink-100 text-ink-600'}`}
                    >
                      {practice.status}
                    </span>
                  </td>
                  <td className="py-2 text-right">
                    <div className="flex justify-end gap-2">
                      {practice.status === 'draft' && (
                        <button
                          className="btn-secondary"
                          disabled={publishPractice.isPending}
                          onClick={() => publishPractice.mutate(practice.id)}
                        >
                          {t('practicesAdminPage.publish')}
                        </button>
                      )}
                      <button
                        className="btn-secondary"
                        disabled={narrationLoadingSlug === practice.slug}
                        onClick={() => void handleGenerateNarrations(practice.slug)}
                      >
                        {narrationLoadingSlug === practice.slug
                          ? t('practicesAdminPage.narration.generating')
                          : t('practicesAdminPage.narration.generateButton')}
                      </button>
                    </div>
                  </td>
                </tr>
                {narrationResults[practice.slug] && (
                  <tr className="border-b border-ink-50 bg-ink-50/40">
                    <td colSpan={4} className="py-2">
                      <ul className="flex flex-wrap gap-3 text-xs">
                        {narrationResults[practice.slug].map((item) => (
                          <li
                            key={item.lang}
                            className={item.status === 'ok' ? 'text-emerald-700' : 'text-rose-600'}
                          >
                            {item.status === 'ok' ? (
                              <>
                                ✓ {item.lang.toUpperCase()}
                                {item.cached
                                  ? ` (${t('practicesAdminPage.narration.cached')})`
                                  : ` (${t('practicesAdminPage.narration.generated')})`}
                              </>
                            ) : (
                              <>
                                ✗ {item.lang.toUpperCase()}: {item.message}
                              </>
                            )}
                          </li>
                        ))}
                      </ul>
                    </td>
                  </tr>
                )}
              </Fragment>
            ))}
          </tbody>
        </table>
      </div>

      {data && data.totalPages > 1 && (
        <div className="mt-4 flex items-center justify-center gap-3">
          <button
            className="btn-secondary"
            disabled={page <= 1}
            onClick={() => setPage((p) => p - 1)}
          >
            {t('practicesAdminPage.pagination.previous')}
          </button>
          <span className="text-sm text-ink-500">
            {t('practicesAdminPage.pagination.pageOf', {
              page: data.page,
              totalPages: data.totalPages,
            })}
          </span>
          <button
            className="btn-secondary"
            disabled={page >= data.totalPages}
            onClick={() => setPage((p) => p + 1)}
          >
            {t('practicesAdminPage.pagination.next')}
          </button>
        </div>
      )}
    </div>
  );
}
