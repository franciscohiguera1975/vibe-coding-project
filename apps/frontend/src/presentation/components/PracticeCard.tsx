import type { PracticeSummary } from '@/domain/entities/practice';
import { getPracticeTypeCover } from '@/presentation/practices/type-images';
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
      className="card group flex flex-col overflow-hidden transition-shadow hover:shadow-md"
    >
      <div className="relative h-40 overflow-hidden">
        <img
          src={getPracticeTypeCover(practice.type, practice.id)}
          alt=""
          className="h-full w-full object-cover transition-transform duration-500 group-hover:scale-105"
        />
        <div className="absolute inset-x-0 bottom-0 flex items-center justify-between gap-2 bg-gradient-to-t from-navy-950/80 to-transparent p-3">
          <span className="badge bg-white/90 text-brand-700">
            {TYPE_LABEL[practice.type] ?? practice.type}
          </span>
          <span
            className={`badge ${DIFFICULTY_COLOR[practice.difficulty] ?? 'bg-ink-100 text-ink-600'}`}
          >
            {DIFFICULTY_LABEL[practice.difficulty] ?? practice.difficulty}
          </span>
        </div>
      </div>
      <div className="flex flex-1 flex-col p-5">
        <h3 className="text-lg font-semibold text-ink-900 group-hover:text-brand-700">
          {practice.title}
        </h3>
        <p className="mt-2 line-clamp-3 flex-1 text-sm text-ink-500">{practice.description}</p>
        <div className="mt-4 flex items-center justify-between text-xs text-ink-400">
          <span className="flex items-center gap-1">
            <svg viewBox="0 0 24 24" className="h-3.5 w-3.5" fill="none" stroke="currentColor" strokeWidth={2}>
              <circle cx="12" cy="12" r="9" />
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 7v5l3 3" />
            </svg>
            {practice.estimatedTimeMinutes} min
          </span>
          <span className="flex flex-wrap justify-end gap-1">
            {practice.technologies.slice(0, 2).map((tech) => (
              <span key={tech} className="rounded bg-ink-50 px-1.5 py-0.5">
                {tech}
              </span>
            ))}
          </span>
        </div>
      </div>
    </Link>
  );
}
