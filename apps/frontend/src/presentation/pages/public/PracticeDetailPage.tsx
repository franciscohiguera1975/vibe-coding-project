import { useAuth } from '@/application/hooks/auth-context';
import {
  useEvaluatePractice,
  usePractice,
  useStartPractice,
  useSubmitPractice,
} from '@/application/hooks/use-practices';
import type { PracticeAttempt, PracticeEvaluation } from '@/domain/entities/practice';
import { getPracticeRunner } from '@/presentation/practices/registry';
import { useState } from 'react';
import { Link, useParams } from 'react-router-dom';

const DIFFICULTY_LABEL: Record<string, string> = {
  beginner: 'Principiante',
  intermediate: 'Intermedio',
  advanced: 'Avanzado',
};

export function PracticeDetailPage() {
  const { slug } = useParams<{ slug: string }>();
  const { user } = useAuth();
  const { data: practice, isLoading, isError } = usePractice(slug);

  const startPractice = useStartPractice();
  const submitPractice = useSubmitPractice();
  const evaluatePractice = useEvaluatePractice();

  const [attempt, setAttempt] = useState<PracticeAttempt | null>(null);
  const [evaluation, setEvaluation] = useState<PracticeEvaluation | null>(null);

  if (isLoading) {
    return <p className="mx-auto max-w-3xl px-4 py-16 text-sm text-ink-500">Cargando...</p>;
  }

  if (isError || !practice) {
    return (
      <div className="mx-auto max-w-3xl px-4 py-16 text-center">
        <h1 className="text-xl font-semibold text-ink-900">Práctica no encontrada</h1>
        <Link to="/catalogo" className="btn-primary mt-4 inline-flex">
          Volver al catálogo
        </Link>
      </div>
    );
  }

  const Runner = getPracticeRunner(practice.type);

  async function handleStart() {
    if (!slug) return;
    const newAttempt = await startPractice.mutateAsync(slug);
    setAttempt(newAttempt);
    setEvaluation(null);
  }

  async function handleSubmit(payload: Record<string, unknown>) {
    if (!attempt) return;
    const submission = await submitPractice.mutateAsync({ attemptId: attempt.id, payload });
    const result = await evaluatePractice.mutateAsync(submission.id);
    setEvaluation(result);
  }

  return (
    <div className="mx-auto max-w-4xl px-4 py-12 sm:px-6 lg:px-8">
      <div className="flex flex-wrap items-center gap-2">
        <span className="badge bg-brand-50 text-brand-700">{practice.type}</span>
        <span className="badge bg-ink-100 text-ink-600">
          {DIFFICULTY_LABEL[practice.difficulty] ?? practice.difficulty}
        </span>
        <span className="text-xs text-ink-400">{practice.estimatedTimeMinutes} min</span>
      </div>

      <h1 className="mt-3 text-3xl font-bold text-ink-900">{practice.title}</h1>
      <p className="mt-2 text-ink-600">{practice.description}</p>

      {practice.objectives.length > 0 && (
        <div className="mt-6">
          <h2 className="text-sm font-semibold uppercase tracking-wide text-ink-500">Objetivos</h2>
          <ul className="mt-2 list-inside list-disc space-y-1 text-sm text-ink-700">
            {practice.objectives.map((objective) => (
              <li key={objective}>{objective}</li>
            ))}
          </ul>
        </div>
      )}

      <div className="mt-6">
        <h2 className="text-sm font-semibold uppercase tracking-wide text-ink-500">
          Instrucciones
        </h2>
        <p className="mt-2 whitespace-pre-line text-sm text-ink-700">{practice.instructions}</p>
      </div>

      <div className="mt-8 border-t border-ink-100 pt-8">
        {!user && (
          <div className="card p-5 text-sm text-ink-600">
            <Link
              to="/login"
              state={{ from: `/catalogo/${slug}` }}
              className="font-medium text-brand-600"
            >
              Inicie sesión
            </Link>{' '}
            para comenzar esta práctica.
          </div>
        )}

        {user && !attempt && (
          <button className="btn-primary" onClick={handleStart} disabled={startPractice.isPending}>
            {startPractice.isPending ? 'Iniciando...' : 'Iniciar práctica'}
          </button>
        )}

        {user && attempt && !evaluation && (
          <Runner
            practice={practice}
            onSubmit={handleSubmit}
            isSubmitting={submitPractice.isPending || evaluatePractice.isPending}
          />
        )}

        {evaluation && (
          <div className="card p-5">
            <h2 className="font-semibold text-ink-900">
              Resultado: {evaluation.passed ? 'Aprobado' : 'No aprobado'} ({evaluation.score}/100)
            </h2>
            <p className="mt-2 text-sm text-ink-600">{evaluation.feedback}</p>
            <button
              className="btn-secondary mt-4"
              onClick={() => {
                setAttempt(null);
                setEvaluation(null);
              }}
            >
              Intentar de nuevo
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
