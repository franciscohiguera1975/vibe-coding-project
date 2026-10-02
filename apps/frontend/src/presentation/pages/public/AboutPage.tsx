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
    <div className="mx-auto max-w-4xl px-4 py-16 sm:px-6 lg:px-8">
      <h1 className="text-3xl font-bold text-ink-900">Acerca de la plataforma</h1>
      <p className="mt-4 text-ink-600">
        Vibe Coding Platform es una plataforma educativa para practicar desarrollo de software y
        manejo de imágenes con apoyo de inteligencia artificial. Las prácticas son reutilizables,
        desacopladas de un proveedor de IA concreto, y pueden integrarse en Moodle u otros LMS
        mediante iframe o API.
      </p>

      <h2 className="mt-10 text-xl font-semibold text-ink-900">Cómo funciona una práctica</h2>
      <ol className="mt-4 space-y-4">
        {STEPS.map((step, index) => (
          <li key={step.title} className="flex gap-4">
            <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-brand-600 text-sm font-semibold text-white">
              {index + 1}
            </span>
            <div>
              <p className="font-medium text-ink-900">{step.title}</p>
              <p className="text-sm text-ink-500">{step.description}</p>
            </div>
          </li>
        ))}
      </ol>
    </div>
  );
}
