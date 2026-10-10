import { useValidateSyllabus, useValidateSyllabusFile } from '@/application/hooks/use-rag';
import type { ChecklistItemResult } from '@/domain/entities/rag';
import { PageHeader } from '@/presentation/components/PageHeader';
import { FormEvent, useRef, useState } from 'react';
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

type InputMode = 'text' | 'file';

export function SyllabusValidationPage() {
  const { t } = useTranslation();
  const [mode, setMode] = useState<InputMode>('text');
  const [text, setText] = useState('');
  const [file, setFile] = useState<File | null>(null);
  const [fileTypeError, setFileTypeError] = useState(false);
  const [results, setResults] = useState<ChecklistItemResult[] | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const textMutation = useValidateSyllabus();
  const fileMutation = useValidateSyllabusFile();

  const isPending = textMutation.isPending || fileMutation.isPending;

  const handleTextSubmit = (e: FormEvent) => {
    e.preventDefault();
    if (!text.trim()) return;
    textMutation.mutate(text, { onSuccess: setResults });
  };

  const handleFileSubmit = (e: FormEvent) => {
    e.preventDefault();
    if (!file) return;
    if (!file.name.toLowerCase().endsWith('.docx')) {
      setFileTypeError(true);
      return;
    }
    setFileTypeError(false);
    fileMutation.mutate(file, {
      onSuccess: (data) => {
        setResults(data);
        setFile(null);
        if (fileInputRef.current) fileInputRef.current.value = '';
      },
    });
  };

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

        <div className="mt-6 flex gap-2" role="tablist">
          <button
            type="button"
            role="tab"
            aria-selected={mode === 'text'}
            className={mode === 'text' ? 'btn-primary' : 'btn-secondary'}
            onClick={() => setMode('text')}
          >
            {t('syllabusValidationPage.modeToggle.pasteText')}
          </button>
          <button
            type="button"
            role="tab"
            aria-selected={mode === 'file'}
            className={mode === 'file' ? 'btn-primary' : 'btn-secondary'}
            onClick={() => setMode('file')}
          >
            {t('syllabusValidationPage.modeToggle.uploadFile')}
          </button>
        </div>

        {mode === 'text' && (
          <form className="mt-4 card p-5" onSubmit={handleTextSubmit}>
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
              <button
                type="submit"
                className="btn-primary"
                disabled={isPending || !text.trim()}
              >
                {textMutation.isPending
                  ? t('syllabusValidationPage.submitting')
                  : t('syllabusValidationPage.submit')}
              </button>
              {textMutation.isError && (
                <span className="text-sm text-rose-600">{t('syllabusValidationPage.error')}</span>
              )}
            </div>
          </form>
        )}

        {mode === 'file' && (
          <form className="mt-4 card p-5" onSubmit={handleFileSubmit}>
            <label className="text-sm font-semibold text-navy-900" htmlFor="syllabus-file">
              {t('syllabusValidationPage.fileLabel')}
            </label>
            <input
              id="syllabus-file"
              ref={fileInputRef}
              type="file"
              accept=".docx"
              className="input mt-2 w-full"
              onChange={(e) => {
                setFile(e.target.files?.[0] ?? null);
                setFileTypeError(false);
              }}
            />
            <p className="mt-2 text-xs text-ink-400">{t('syllabusValidationPage.fileInputHint')}</p>
            <div className="mt-4 flex items-center gap-3">
              <button type="submit" className="btn-primary" disabled={isPending || !file}>
                {fileMutation.isPending
                  ? t('syllabusValidationPage.fileSubmitting')
                  : t('syllabusValidationPage.fileSubmit')}
              </button>
              {fileTypeError && (
                <span className="text-sm text-rose-600">
                  {t('syllabusValidationPage.fileTypeError')}
                </span>
              )}
              {!fileTypeError && fileMutation.isError && (
                <span className="text-sm text-rose-600">{t('syllabusValidationPage.error')}</span>
              )}
            </div>
          </form>
        )}

        {results && (
          <div className="mt-10">
            <h2 className="text-xl font-bold text-navy-900">
              {t('syllabusValidationPage.resultsHeading')}
            </h2>
            <div className="mt-6 grid grid-cols-1 gap-5 md:grid-cols-2">
              {results.map((result) => (
                <ChecklistResultCard key={result.item} result={result} />
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
