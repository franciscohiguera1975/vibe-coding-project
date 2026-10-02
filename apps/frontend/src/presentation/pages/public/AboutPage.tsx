import { AboutIntro } from '@/presentation/components/AboutIntro';
import { FeatureHighlights } from '@/presentation/components/FeatureHighlights';
import { PageHeader } from '@/presentation/components/PageHeader';

const STEPS = [
  {
    title: 'Seleccione una práctica',
    description: 'Explore el catálogo filtrado por tipo, nivel o tecnología.',
  },
  {
    title: 'Lea los objetivos',
    description: 'Cada práctica declara qué va a aprender y qué se espera de usted.',
  },
  {
    title: 'Realice la actividad',
    description: 'Siga las instrucciones y use el contenido interactivo de la práctica.',
  },
  {
    title: 'Envíe su resultado',
    description: 'Su envío se evalúa contra criterios explícitos definidos por la práctica.',
  },
  {
    title: 'Reciba retroalimentación',
    description: 'Vea su puntaje, el detalle de la evaluación y sugerencias de un tutor de IA.',
  },
];

export function AboutPage() {
  return (
    <div>
      <PageHeader
        title="Acerca de la plataforma"
        breadcrumbs={[{ label: 'Inicio', to: '/' }, { label: 'La plataforma' }]}
      />

      <FeatureHighlights />
      <AboutIntro showCta={false} />

      <div className="mx-auto max-w-4xl px-4 py-16 sm:px-6 lg:px-8">
        <span className="inline-flex items-center gap-2 text-sm font-semibold uppercase tracking-wide text-brand-600">
          <span className="h-0.5 w-8 bg-brand-500" /> Paso a paso
        </span>
        <h2 className="mt-3 text-2xl font-bold text-navy-900">Cómo funciona una práctica</h2>
        <ol className="mt-6 space-y-5">
          {STEPS.map((step, index) => (
            <li key={step.title} className="flex gap-4">
              <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-brand-500 text-sm font-semibold text-white">
                {index + 1}
              </span>
              <div>
                <p className="font-semibold text-navy-900">{step.title}</p>
                <p className="text-sm text-ink-500">{step.description}</p>
              </div>
            </li>
          ))}
        </ol>
      </div>
    </div>
  );
}
