import { useAnalyzeImage } from '@/application/hooks/use-images';
import type { PracticeRunnerProps } from '@/presentation/practices/types';
import { useState } from 'react';
import { useTranslation } from 'react-i18next';

interface ImageSlotState {
  previewUrl?: string;
  count?: number;
  warnings?: string[];
  isAnalyzing?: boolean;
}

export function ImagePracticeRunner({ practice, onSubmit, isSubmitting }: PracticeRunnerProps) {
  const { t } = useTranslation();
  const evaluation = practice.evaluation as {
    strategy?: string;
    reference?: Record<string, number>;
  };
  const content = practice.content as {
    counting_rule?: { counts?: string; excludes?: string[]; illegible_when?: string[] };
    required_output?: string[];
  };

  const imageIds = Object.keys(evaluation.reference ?? {});
  const [slots, setSlots] = useState<Record<string, ImageSlotState>>({});
  const [report, setReport] = useState('');
  const analyzeImage = useAnalyzeImage();

  async function handleFileSelected(imageId: string, file: File | undefined) {
    if (!file) return;
    const previewUrl = URL.createObjectURL(file);
    setSlots((s) => ({ ...s, [imageId]: { previewUrl, isAnalyzing: true } }));
    try {
      const result = await analyzeImage.mutateAsync({ slug: practice.slug, file });
      setSlots((s) => ({
        ...s,
        [imageId]: {
          previewUrl,
          count: result.count,
          warnings: result.warnings,
          isAnalyzing: false,
        },
      }));
    } catch {
      setSlots((s) => ({
        ...s,
        [imageId]: { previewUrl, isAnalyzing: false, warnings: [t('imagePracticeRunner.analyzeError')] },
      }));
    }
  }

  function handleCountOverride(imageId: string, value: string) {
    setSlots((s) => ({ ...s, [imageId]: { ...s[imageId], count: Number(value) } }));
  }

  async function handleSubmitCounts() {
    const payload = {
      counts: Object.fromEntries(imageIds.map((id) => [id, slots[id]?.count ?? 0])),
    };
    await onSubmit(payload);
  }

  async function handleSubmitReport() {
    await onSubmit({ report });
  }

  return (
    <div className="space-y-6">
      {content.counting_rule && (
        <div className="card p-5">
          <h3 className="font-semibold text-ink-900">
            {t('imagePracticeRunner.countingRule.heading')}
          </h3>
          <p className="mt-1 text-sm text-ink-600">
            {t('imagePracticeRunner.countingRule.counts', { value: content.counting_rule.counts })}
          </p>
          {content.counting_rule.excludes && (
            <p className="mt-1 text-sm text-ink-500">
              {t('imagePracticeRunner.countingRule.excludes', {
                value: content.counting_rule.excludes.join(', '),
              })}
            </p>
          )}
          {content.counting_rule.illegible_when && (
            <p className="mt-1 text-sm text-ink-500">
              {t('imagePracticeRunner.countingRule.illegibleWhen', {
                value: content.counting_rule.illegible_when.join(', '),
              })}
            </p>
          )}
        </div>
      )}

      {evaluation.strategy === 'count_comparison' && imageIds.length > 0 && (
        <div className="card p-5">
          <h3 className="font-semibold text-ink-900">
            {t('imagePracticeRunner.countPerImage.heading')}
          </h3>
          <p className="mt-1 text-xs text-ink-500">
            {t('imagePracticeRunner.countPerImage.description')}
          </p>
          <div className="mt-3 grid grid-cols-1 gap-4 sm:grid-cols-2">
            {imageIds.map((id) => {
              const slot = slots[id] ?? {};
              return (
                <div key={id} className="rounded-lg border border-ink-100 p-3">
                  <label className="label">{id}</label>
                  <input
                    type="file"
                    accept="image/png,image/jpeg,image/webp"
                    className="input text-xs"
                    onChange={(e) => handleFileSelected(id, e.target.files?.[0])}
                  />
                  {slot.previewUrl && (
                    <img
                      src={slot.previewUrl}
                      alt={t('imagePracticeRunner.previewAlt', { id })}
                      className="mt-2 h-24 w-full rounded object-cover"
                    />
                  )}
                  {slot.isAnalyzing && (
                    <p className="mt-1 text-xs text-ink-400">{t('imagePracticeRunner.analyzing')}</p>
                  )}
                  {slot.warnings && slot.warnings.length > 0 && (
                    <p className="mt-1 text-xs text-amber-700">⚠ {slot.warnings.join('; ')}</p>
                  )}
                  <div className="mt-2">
                    <label className="label">{t('imagePracticeRunner.proposedCountLabel')}</label>
                    <input
                      type="number"
                      min={0}
                      className="input"
                      value={slot.count ?? ''}
                      onChange={(e) => handleCountOverride(id, e.target.value)}
                    />
                  </div>
                </div>
              );
            })}
          </div>
          <button className="btn-primary mt-4" onClick={handleSubmitCounts} disabled={isSubmitting}>
            {isSubmitting
              ? t('imagePracticeRunner.submitCounts.submitting')
              : t('imagePracticeRunner.submitCounts.button')}
          </button>
        </div>
      )}

      {evaluation.strategy === 'manual' && (
        <div className="card p-5">
          <h3 className="font-semibold text-ink-900">{t('imagePracticeRunner.report.heading')}</h3>
          {content.required_output && (
            <ul className="mt-1 list-inside list-disc text-sm text-ink-500">
              {content.required_output.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          )}
          <textarea
            className="input mt-3"
            rows={6}
            placeholder={t('imagePracticeRunner.report.placeholder')}
            value={report}
            onChange={(e) => setReport(e.target.value)}
          />
          <button
            className="btn-primary mt-3"
            onClick={handleSubmitReport}
            disabled={isSubmitting || !report.trim()}
          >
            {isSubmitting
              ? t('imagePracticeRunner.report.submitting')
              : t('imagePracticeRunner.report.submit')}
          </button>
          <p className="mt-2 text-xs text-ink-400">
            {t('imagePracticeRunner.report.reviewNotice')}
          </p>
        </div>
      )}
    </div>
  );
}
