import { usePractices } from '@/application/hooks/use-practices';
import { PracticeCard } from '@/presentation/components/PracticeCard';
import { Link } from 'react-router-dom';

const HIGHLIGHTS = [
  {
    title: 'Vibe Coding guiado',
    description:
      'Practique desarrollo de software asistido por IA con instrucciones claras y criterios de evaluación explícitos.',
  },
  {
    title: 'Manejo de imágenes',
    description:
      'Construya y evalúe prototipos de análisis de imágenes, comparando sus resultados contra una referencia humana.',
  },
  {
    title: 'Tutor con IA',
    description:
      'Reciba pistas y retroalimentación de un agente con herramientas controladas, trazabilidad y límites claros.',
  },
];

export function HomePage() {
  const { data } = usePractices({ status: 'published' }, 1, 3);

  return (
    <div>
      <section className="bg-gradient-to-br from-brand-700 via-brand-600 to-brand-500">
        <div className="mx-auto max-w-7xl px-4 py-20 sm:px-6 lg:px-8">
          <div className="max-w-2xl">
            <span className="badge bg-white/15 text-white">Curso Vibe Coding · CEDIA 2026</span>
            <h1 className="mt-4 text-4xl font-bold tracking-tight text-white sm:text-5xl">
              Aprenda a construir software con IA, practicando de verdad.
            </h1>
            <p className="mt-4 text-lg text-brand-50">
              Prácticas interactivas de desarrollo de software y manejo de imágenes, con
              retroalimentación de un tutor de IA y evaluación basada en criterios explícitos.
            </p>
            <div className="mt-8 flex flex-wrap gap-3">
              <Link
                to="/catalogo"
                className="btn-primary bg-white text-brand-700 hover:bg-brand-50"
              >
                Explorar el catálogo
              </Link>
              <Link to="/acerca" className="btn-secondary bg-transparent text-white ring-white/40">
                Cómo funciona
              </Link>
            </div>
          </div>
        </div>
      </section>

      <section className="mx-auto max-w-7xl px-4 py-16 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 gap-8 sm:grid-cols-3">
          {HIGHLIGHTS.map((item) => (
            <div key={item.title} className="card p-6">
              <h3 className="text-lg font-semibold text-ink-900">{item.title}</h3>
              <p className="mt-2 text-sm text-ink-500">{item.description}</p>
            </div>
          ))}
        </div>
      </section>

      {data && data.items.length > 0 && (
        <section className="bg-white py-16">
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
            <div className="flex items-end justify-between">
              <h2 className="text-2xl font-semibold text-ink-900">Prácticas destacadas</h2>
              <Link
                to="/catalogo"
                className="text-sm font-medium text-brand-600 hover:text-brand-700"
              >
                Ver todas →
              </Link>
            </div>
            <div className="mt-6 grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
              {data.items.map((practice) => (
                <PracticeCard key={practice.id} practice={practice} />
              ))}
            </div>
          </div>
        </section>
      )}
    </div>
  );
}
