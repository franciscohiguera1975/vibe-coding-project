import type { PracticeRunnerProps } from '@/presentation/practices/types';
import { useState } from 'react';

export function ImagePracticeRunner({ practice, onSubmit, isSubmitting }: PracticeRunnerProps) {
  const evaluation = practice.evaluation as {
    strategy?: string;
    reference?: Record<string, number>;
  };
  const content = practice.content as {
    counting_rule?: { counts?: string; excludes?: string[]; illegible_when?: string[] };
    required_output?: string[];
  };

  const imageIds = Object.keys(evaluation.reference ?? {});
  const [counts, setCounts] = useState<Record<string, string>>({});
  const [report, setReport] = useState('');

  async function handleSubmitCounts() {
    const payload = {
      counts: Object.fromEntries(imageIds.map((id) => [id, Number(counts[id] ?? 0)])),
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
          <h3 className="font-semibold text-ink-900">Regla de conteo</h3>
          <p className="mt-1 text-sm text-ink-600">Cuenta: {content.counting_rule.counts}</p>
          {content.counting_rule.excludes && (
            <p className="mt-1 text-sm text-ink-500">
              No cuenta: {content.counting_rule.excludes.join(', ')}
            </p>
          )}
          {content.counting_rule.illegible_when && (
            <p className="mt-1 text-sm text-ink-500">
              Ilegible cuando: {content.counting_rule.illegible_when.join(', ')}
            </p>
          )}
        </div>
      )}

      {evaluation.strategy === 'count_comparison' && imageIds.length > 0 && (
        <div className="card p-5">
          <h3 className="font-semibold text-ink-900">Conteo por imagen</h3>
          <p className="mt-1 text-xs text-ink-500">
            Las imágenes de referencia se gestionan desde el panel de administración; ingrese su
            conteo para cada identificador.
          </p>
          <div className="mt-3 grid grid-cols-2 gap-3 sm:grid-cols-4">
            {imageIds.map((id) => (
              <div key={id}>
                <label className="label">{id}</label>
                <input
                  type="number"
                  min={0}
                  className="input"
                  value={counts[id] ?? ''}
                  onChange={(e) => setCounts((c) => ({ ...c, [id]: e.target.value }))}
                />
              </div>
            ))}
          </div>
          <button className="btn-primary mt-4" onClick={handleSubmitCounts} disabled={isSubmitting}>
            {isSubmitting ? 'Enviando...' : 'Enviar conteo'}
          </button>
        </div>
      )}

      {evaluation.strategy === 'manual' && (
        <div className="card p-5">
          <h3 className="font-semibold text-ink-900">Informe</h3>
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
            placeholder="Describa su diagnóstico, errores anotados y propuesta de ajuste..."
            value={report}
            onChange={(e) => setReport(e.target.value)}
          />
          <button
            className="btn-primary mt-3"
            onClick={handleSubmitReport}
            disabled={isSubmitting || !report.trim()}
          >
            {isSubmitting ? 'Enviando...' : 'Enviar informe'}
          </button>
          <p className="mt-2 text-xs text-ink-400">
            Esta práctica requiere revisión de un docente; el envío queda registrado para esa
            revisión.
          </p>
        </div>
      )}
    </div>
  );
}
