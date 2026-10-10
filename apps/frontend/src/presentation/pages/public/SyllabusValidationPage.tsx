import { useValidateSyllabus } from '@/application/hooks/use-rag';
import type { ChecklistItemResult } from '@/domain/entities/rag';
import { PageHeader } from '@/presentation/components/PageHeader';
import { useState } from 'react';
import { useTranslation } from 'react-i18next';

function ComplianceBadge({ cumple }: { cumple: boolean | null }) {
  const { t } = useTranslation();
  if (cumple === true) {
    return (
      <span className="inline-flex items-center rounded-full bg-emerald-100 px-3 py-1 text-xs font-semibold text-emerald-700">
        {t('syllabusValidationPage.badge.compliant')}
      </span>
    );
  }
  if (cumple === false) {
    return (
      <span className="inline-flex items-center rounded-full bg-rose-100 px-3 py-1 text-xs font-semibold text-rose-700">
        {t('syllabusValidationPage.badge.nonCompliant')}
      </span>
    );
  }
  return (
    <span className="inline-flex items-center rounded-full bg-ink-100 px-3 py-1 text-xs font-semibold text-ink-600">
      {t('syllabusValidationPage.badge.undetermined')}
    </span>
  );
}

function ChecklistResultCard({ result }: { result: ChecklistItemResult }) {
  const { t } = useTranslation();
  return (
    <div className="card p-5">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <h3 className="font-semibold text-navy-900">{result.label}</h3>
        <ComplianceBadge cumple={result.cumple} />
      </div>
      <p className="mt-3 text-sm text-ink-600">{result.explicacion}</p>
      {result.citas.length > 0 && (
        <div className="mt-4 border-t border-ink-100 pt-3">
          <p className="text-xs font-semibold uppercase tracking-wide text-ink-400">
            {t('syllabusValidationPage.citationsLabel')}
          </p>
          <ul className="mt-2 space-y-1">
            {result.citas.map((cita, idx) => (
              <li key={idx} className="text-xs text-ink-500">
                {cita.sourceDocument} — {cita.articleLabel}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

export function SyllabusValidationPage() {
  const { t } = useTranslation();
  const [text, setText] = useState('');
  const { mutate, data, isPending, isError } = useValidateSyllabus();

  return (
    <div>
      <PageHeader
        title={t('syllabusValidationPage.pageTitle')}
        breadcrumbs={[
          { label: t('syllabusValidationPage.breadcrumbs.home'), to: '/' },
          { label: t('syllabusValidationPage.breadcrumbs.current') },
        ]}
      />

      <div className="mx-auto max-w-5xl px-4 py-12 sm:px-6 lg:px-8">
        <p className="max-w-3xl text-ink-500">{t('syllabusValidationPage.description')}</p>

        <form
          className="mt-6 card p-5"
          onSubmit={(e) => {
            e.preventDefault();
            if (text.trim()) mutate(text);
          }}
        >
          <label className="text-sm font-semibold text-navy-900" htmlFor="syllabus-text">
            {t('syllabusValidationPage.textareaLabel')}
          </label>
          <textarea
            id="syllabus-text"
            className="input mt-2 min-h-[220px] w-full"
            placeholder={t('syllabusValidationPage.textareaPlaceholder')}
            value={text}
            onChange={(e) => setText(e.target.value)}
          />
          <div className="mt-4 flex items-center gap-3">
            <button type="submit" className="btn-primary" disabled={isPending || !text.trim()}>
              {isPending
                ? t('syllabusValidationPage.submitting')
                : t('syllabusValidationPage.submit')}
            </button>
            {isError && (
              <span className="text-sm text-rose-600">{t('syllabusValidationPage.error')}</span>
            )}
          </div>
        </form>

        {data && (
          <div className="mt-10">
            <h2 className="text-xl font-bold text-navy-900">
              {t('syllabusValidationPage.resultsHeading')}
            </h2>
            <div className="mt-6 grid grid-cols-1 gap-5 md:grid-cols-2">
              {data.map((result) => (
                <ChecklistResultCard key={result.item} result={result} />
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
