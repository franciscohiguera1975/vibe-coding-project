import type { PracticeRunnerProps } from '@/presentation/practices/types';
import { useMemo, useState } from 'react';
import { Trans, useTranslation } from 'react-i18next';

interface Variable {
  label?: string;
  unit?: string;
  min?: number;
  max?: number;
}

interface WorkedExample {
  speed_kmh: number;
  time_h: number;
  distance_km: number;
}

interface EvaluationCheck {
  field: string;
  expected: number;
  tolerance?: number;
}

function humanizeField(field: string): string {
  return field.replace(/_/g, ' ');
}

export function SoftwarePracticeRunner({ practice, onSubmit, isSubmitting }: PracticeRunnerProps) {
  const { t } = useTranslation();
  const content = practice.content as {
    model?: { variables?: Record<string, Variable>; assumptions?: string[] };
    worked_examples?: WorkedExample[];
    transfer_question?: string;
    buggy_version_description?: Record<string, string>;
    acceptance_criteria?: string[];
  };
  const checks = useMemo(
    () =>
      ((practice.evaluation as { checks?: EvaluationCheck[] }).checks ?? []) as EvaluationCheck[],
    [practice.evaluation],
  );

  const variables = content.model?.variables ?? {};
  const hasSimulator = 'speed_kmh' in variables && 'time_h' in variables;

  const [predicted, setPredicted] = useState<string>('');
  const [speed, setSpeed] = useState(60);
  const [time, setTime] = useState(2);
  const [executed, setExecuted] = useState(false);

  const result = useMemo(() => speed * time, [speed, time]);

  // Para practicas con worked_examples (p.ej. software-01), los valores enviados se
  // calculan automaticamente con el mismo modelo — la practica evalua que la
  // herramienta calcule bien, no que el estudiante adivine el resultado.
  const autoValues = useMemo(() => {
    const values: Record<string, number> = {};
    (content.worked_examples ?? []).forEach((example, index) => {
      const field = `distance_km_case${index + 1}`;
      if (checks.some((c) => c.field === field)) {
        values[field] = example.speed_kmh * example.time_h;
      }
    });
    return values;
  }, [content.worked_examples, checks]);

  const manualFields = checks.filter((c) => !(c.field in autoValues));
  const [manualValues, setManualValues] = useState<Record<string, string>>({});

  async function handleSubmit() {
    const payload: Record<string, unknown> = { ...autoValues };
    for (const check of manualFields) {
      payload[check.field] = Number(manualValues[check.field] ?? 0);
    }
    await onSubmit(payload);
  }

  return (
    <div className="space-y-6">
      {hasSimulator && (
        <div className="card p-5">
          <h3 className="font-semibold text-ink-900">
            {t('softwarePracticeRunner.simulation.heading')}
          </h3>
          {content.model?.assumptions && (
            <p className="mt-1 text-xs text-ink-400">
              {t('softwarePracticeRunner.simulation.assumptions', {
                value: content.model.assumptions.join(', '),
              })}
            </p>
          )}

          <div className="mt-4">
            <label className="label">{t('softwarePracticeRunner.simulation.predictLabel')}</label>
            <input
              type="number"
              className="input max-w-xs"
              value={predicted}
              onChange={(e) => setPredicted(e.target.value)}
              placeholder={t('softwarePracticeRunner.simulation.predictPlaceholder')}
            />
          </div>

          <div className="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-2">
            <div>
              <label className="label" htmlFor="speed-range">
                {t('softwarePracticeRunner.simulation.speedLabel', {
                  unit: variables.speed_kmh?.unit ?? 'km/h',
                })}
              </label>
              <input
                id="speed-range"
                type="range"
                min={variables.speed_kmh?.min ?? 0}
                max={variables.speed_kmh?.max ?? 100}
                value={speed}
                disabled={!predicted}
                onChange={(e) => setSpeed(Number(e.target.value))}
                className="w-full"
              />
              <span className="text-sm text-ink-500">{speed} km/h</span>
            </div>
            <div>
              <label className="label" htmlFor="time-range">
                {t('softwarePracticeRunner.simulation.timeLabel', {
                  unit: variables.time_h?.unit ?? 'h',
                })}
              </label>
              <input
                id="time-range"
                type="range"
                step={0.5}
                min={variables.time_h?.min ?? 0}
                max={variables.time_h?.max ?? 3}
                value={time}
                disabled={!predicted}
                onChange={(e) => setTime(Number(e.target.value))}
                className="w-full"
              />
              <span className="text-sm text-ink-500">{time} h</span>
            </div>
          </div>

          <button
            className="btn-primary mt-4"
            disabled={!predicted}
            onClick={() => setExecuted(true)}
          >
            {t('softwarePracticeRunner.simulation.calculate')}
          </button>

          {executed && (
            <div className="mt-4 rounded-lg bg-ink-50 p-4">
              <p className="text-sm text-ink-700">
                <Trans
                  i18nKey="softwarePracticeRunner.simulation.resultText"
                  values={{ result, speed, time }}
                  components={{ strong: <strong /> }}
                />
              </p>
              <div className="mt-2 h-3 w-full rounded-full bg-ink-200">
                <div
                  className="h-3 rounded-full bg-brand-600 transition-all"
                  style={{ width: `${Math.min(100, (result / 300) * 100)}%` }}
                />
              </div>
              {predicted && (
                <p className="mt-2 text-sm text-ink-500">
                  {Number(predicted) !== result
                    ? t('softwarePracticeRunner.simulation.predictionMismatch', { predicted, result })
                    : t('softwarePracticeRunner.simulation.predictionMatch', { predicted, result })}
                </p>
              )}
            </div>
          )}

          {content.transfer_question && (
            <p className="mt-4 text-sm text-ink-600">
              <Trans
                i18nKey="softwarePracticeRunner.simulation.transfer"
                values={{ question: content.transfer_question }}
                components={{ strong: <strong /> }}
              />
            </p>
          )}
        </div>
      )}

      {content.buggy_version_description && (
        <div className="card p-5">
          <h3 className="font-semibold text-ink-900">{t('softwarePracticeRunner.bugs.heading')}</h3>
          <ul className="mt-2 list-inside list-disc space-y-1 text-sm text-ink-600">
            {Object.values(content.buggy_version_description).map((bug) => (
              <li key={bug}>{bug}</li>
            ))}
          </ul>
        </div>
      )}

      {manualFields.length > 0 && (
        <div className="card p-5">
          <h3 className="font-semibold text-ink-900">
            {t('softwarePracticeRunner.selfCheck.heading')}
          </h3>
          <p className="mt-1 text-xs text-ink-500">
            {t('softwarePracticeRunner.selfCheck.description')}
          </p>
          <div className="mt-3 space-y-2">
            {manualFields.map((check) => (
              <div key={check.field} className="flex items-center justify-between gap-3">
                <span className="text-sm text-ink-700">{humanizeField(check.field)}</span>
                <input
                  type="number"
                  className="input w-24"
                  value={manualValues[check.field] ?? ''}
                  onChange={(e) =>
                    setManualValues((v) => ({ ...v, [check.field]: e.target.value }))
                  }
                />
              </div>
            ))}
          </div>
        </div>
      )}

      <button className="btn-primary" onClick={handleSubmit} disabled={isSubmitting}>
        {isSubmitting
          ? t('softwarePracticeRunner.submit.submitting')
          : t('softwarePracticeRunner.submit.button')}
      </button>
    </div>
  );
}
