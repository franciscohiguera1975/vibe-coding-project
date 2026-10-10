import { useAuth } from '@/application/hooks/auth-context';
import { useLatestRagEvaluation, useRunRagEvaluation } from '@/application/hooks/use-rag';
import { PageHeader } from '@/presentation/components/PageHeader';
import { useTranslation } from 'react-i18next';

function MatchMark({ match }: { match: boolean }) {
  return match ? (
    <span className="text-emerald-600" aria-hidden>
      ✓
    </span>
  ) : (
    <span className="text-rose-600" aria-hidden>
      ✗
    </span>
  );
}

function truncate(text: string, max = 140): string {
  return text.length > max ? `${text.slice(0, max)}…` : text;
}

export function RagEvaluationPage() {
  const { t } = useTranslation();
  const { hasPermission } = useAuth();
  const { data, isLoading } = useLatestRagEvaluation();
  const runEvaluation = useRunRagEvaluation();
  const canRun = hasPermission('practice:update');

  return (
    <div>
      <PageHeader
        title={t('ragEvaluationPage.pageTitle')}
        breadcrumbs={[
          { label: t('ragEvaluationPage.breadcrumbs.home'), to: '/' },
          { label: t('ragEvaluationPage.breadcrumbs.current') },
        ]}
      />

      <div className="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <p className="max-w-3xl text-ink-500">{t('ragEvaluationPage.description')}</p>
          {canRun && (
            <button
              type="button"
              className="btn-primary"
              disabled={runEvaluation.isPending}
              onClick={() => runEvaluation.mutate()}
            >
              {runEvaluation.isPending
                ? t('ragEvaluationPage.running')
                : t('ragEvaluationPage.runButton')}
            </button>
          )}
        </div>

        {isLoading && <p className="mt-8 text-sm text-ink-500">{t('ragEvaluationPage.loading')}</p>}

        {!isLoading && !data && (
          <p className="mt-8 text-sm text-ink-500">{t('ragEvaluationPage.empty')}</p>
        )}

        {data && (
          <>
            <div className="mt-8 grid grid-cols-1 gap-4 sm:grid-cols-3">
              <div className="card p-5 text-center">
                <p className="text-3xl font-bold text-navy-900">{data.summary.total}</p>
                <p className="mt-1 text-sm text-ink-500">
                  {t('ragEvaluationPage.stats.total')}
                </p>
              </div>
              <div className="card p-5 text-center">
                <p className="text-3xl font-bold text-emerald-600">
                  {data.summary.ragCitationMatches}/{data.summary.total}
                </p>
                <p className="mt-1 text-sm text-ink-500">
                  {t('ragEvaluationPage.stats.ragMatches')}
                </p>
              </div>
              <div className="card p-5 text-center">
                <p className="text-3xl font-bold text-rose-600">
                  {data.summary.baselineCitationMatches}/{data.summary.total}
                </p>
                <p className="mt-1 text-sm text-ink-500">
                  {t('ragEvaluationPage.stats.baselineMatches')}
                </p>
              </div>
            </div>

            <p className="mt-4 text-sm font-medium text-navy-900">
              {t('ragEvaluationPage.summarySentence', {
                ragMatches: data.summary.ragCitationMatches,
                baselineMatches: data.summary.baselineCitationMatches,
                total: data.summary.total,
              })}
            </p>

            <div className="mt-6 overflow-x-auto">
              <table className="min-w-full divide-y divide-ink-100 text-left text-sm">
                <thead>
                  <tr className="text-xs font-semibold uppercase tracking-wide text-ink-400">
                    <th className="py-2 pr-4">{t('ragEvaluationPage.table.question')}</th>
                    <th className="py-2 pr-4">{t('ragEvaluationPage.table.expectedCitation')}</th>
                    <th className="py-2 pr-4">{t('ragEvaluationPage.table.baseline')}</th>
                    <th className="py-2 pr-4">{t('ragEvaluationPage.table.rag')}</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-ink-100">
                  {data.results.map((row) => (
                    <tr key={row.id} className="align-top">
                      <td className="max-w-xs py-3 pr-4 text-ink-700">{row.question}</td>
                      <td className="py-3 pr-4 text-ink-500">
                        {row.expectedCitation.sourceDocument} — {row.expectedCitation.articleLabel}
                      </td>
                      <td className="max-w-xs py-3 pr-4 text-ink-500">
                        <MatchMark match={row.baselineCitationMatch} />{' '}
                        {truncate(row.baselineAnswer)}
                      </td>
                      <td className="max-w-xs py-3 pr-4 text-ink-500">
                        <MatchMark match={row.ragCitationMatch} /> {truncate(row.ragAnswer)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
