import type { PracticeSummary } from '@/domain/entities/practice';
import { Link } from 'react-router-dom';

const DIFFICULTY_LABEL: Record<string, string> = {
  beginner: 'Principiante',
  intermediate: 'Intermedio',
  advanced: 'Avanzado',
};

const DIFFICULTY_COLOR: Record<string, string> = {
  beginner: 'bg-emerald-50 text-emerald-700',
  intermediate: 'bg-amber-50 text-amber-700',
  advanced: 'bg-rose-50 text-rose-700',
};

const TYPE_LABEL: Record<string, string> = {
  software: 'Desarrollo de software',
  image: 'Manejo de imágenes',
};

export function PracticeCard({ practice }: { practice: PracticeSummary }) {
  return (
    <Link
      to={`/catalogo/${practice.slug}`}
      className="card group flex flex-col p-5 transition-shadow hover:shadow-md"
    >
      <div className="flex items-center justify-between">
        <span className="badge bg-brand-50 text-brand-700">
          {TYPE_LABEL[practice.type] ?? practice.type}
        </span>
        <span
          className={`badge ${DIFFICULTY_COLOR[practice.difficulty] ?? 'bg-ink-100 text-ink-600'}`}
        >
          {DIFFICULTY_LABEL[practice.difficulty] ?? practice.difficulty}
        </span>
      </div>
      <h3 className="mt-3 text-lg font-semibold text-ink-900 group-hover:text-brand-700">
        {practice.title}
      </h3>
      <p className="mt-2 line-clamp-3 flex-1 text-sm text-ink-500">{practice.description}</p>
      <div className="mt-4 flex items-center justify-between text-xs text-ink-400">
        <span>{practice.estimatedTimeMinutes} min</span>
        <span className="flex flex-wrap gap-1">
          {practice.technologies.slice(0, 2).map((tech) => (
            <span key={tech} className="rounded bg-ink-50 px-1.5 py-0.5">
              {tech}
            </span>
          ))}
        </span>
      </div>
    </Link>
  );
}
