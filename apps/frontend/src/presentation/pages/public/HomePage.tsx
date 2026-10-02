import { usePractices } from '@/application/hooks/use-practices';
import categoryImages from '@/assets/home/category-images-practice.jpg';
import categorySoftware from '@/assets/home/category-software.jpg';
import heroImages from '@/assets/home/hero-images-practice.jpg';
import heroSoftware1 from '@/assets/home/hero-software-1.jpg';
import heroSoftware2 from '@/assets/home/hero-software-2.jpg';
import logoUte from '@/assets/logos/ute.png';
import logoUtpl from '@/assets/logos/utpl.png';
import instructor1 from '@/assets/team/instructor1.jpeg';
import instructor2 from '@/assets/team/instructor2.png';
import instructor3 from '@/assets/team/instructor3.jpeg';
import instructor4 from '@/assets/team/instructor4.png';
import { AboutIntro } from '@/presentation/components/AboutIntro';
import { FeatureHighlights } from '@/presentation/components/FeatureHighlights';
import { HeroCarousel, type HeroSlide } from '@/presentation/components/HeroCarousel';
import { PracticeCard } from '@/presentation/components/PracticeCard';
import { Link } from 'react-router-dom';

const SLIDES: HeroSlide[] = [
  {
    image: heroSoftware1,
    eyebrow: 'DESARROLLO DE SOFTWARE',
    title: 'Aprenda a construir software con IA, practicando de verdad',
    description:
      'Prácticas interactivas de Vibe Coding con retroalimentación de un tutor de IA y evaluación basada en criterios explícitos.',
    primaryCta: { label: 'Explorar el catálogo', to: '/catalogo' },
    secondaryCta: { label: 'Cómo funciona', to: '/acerca' },
  },
  {
    image: heroSoftware2,
    eyebrow: 'IA AGÉNTICA',
    title: 'Un tutor de IA con herramientas controladas y trazabilidad total',
    description:
      'Pistas y retroalimentación de un agente con límites claros de iteraciones y tokens — cada decisión queda registrada.',
    primaryCta: { label: 'Conocer al tutor de IA', to: '/acerca' },
    secondaryCta: { label: 'Ver prácticas', to: '/catalogo?type=software' },
  },
  {
    image: heroImages,
    eyebrow: 'MANEJO DE IMÁGENES',
    title: 'Construya prototipos de conteo de objetos con una regla explícita',
    description:
      'Compare sus resultados contra una referencia humana y entienda los límites de lo que un modelo puede inferir de una imagen.',
    primaryCta: { label: 'Prácticas de imágenes', to: '/catalogo?type=image' },
    secondaryCta: { label: 'Cómo funciona', to: '/acerca' },
  },
];

const STEPS = [
  {
    title: 'Elija una práctica',
    description: 'Filtre el catálogo por tipo, nivel o tecnología y lea sus objetivos.',
  },
  {
    title: 'Practique con IA',
    description: 'Construya o depure su solución con asistencia de un tutor de IA bajo demanda.',
  },
  {
    title: 'Envíe y evalúe',
    description: 'Su resultado se evalúa con criterios explícitos: numéricos, de conteo o manuales.',
  },
  {
    title: 'Reciba retroalimentación',
    description: 'Compare su predicción, reciba feedback y vuelva a intentarlo cuantas veces quiera.',
  },
];

const INSTRUCTORS = [
  {
    photo: instructor1,
    name: 'Mtr. Francisco Javier Higuera González',
    role: 'Docente-Investigador',
    org: 'Universidad UTE',
    logo: logoUte,
  },
  {
    photo: instructor2,
    name: 'Mgs. Carlos Byron Bermeo León',
    role: 'Facultad de Ciencias Sociales, Educación y Humanidades · Depto. de Comunicación y Artes',
    org: 'Universidad UTPL',
    logo: logoUtpl,
  },
  {
    photo: instructor3,
    name: 'Mgs. Yamilet García',
    role: 'Docente-Investigador',
    org: 'Universidad UTE',
    logo: logoUte,
  },
  {
    photo: instructor4,
    name: 'Mgs. José Francisco Silva Garcés',
    role: 'Docente-Investigador',
    org: 'Universidad UTE',
    logo: logoUte,
  },
];

const VOICES = [
  {
    initials: 'DS',
    role: 'Estudiante · Desarrollo de software',
    quote:
      'Poder predecir el resultado antes de ejecutarlo me obligó a entender el modelo, no solo a copiar código generado por la IA.',
  },
  {
    initials: 'MI',
    role: 'Estudiante · Manejo de imágenes',
    quote:
      'Comparar mi conteo contra la referencia humana me mostró exactamente dónde fallaba mi regla y cómo corregirla.',
  },
  {
    initials: 'DC',
    role: 'Docente',
    quote:
      'La trazabilidad del tutor de IA — qué herramienta usó y por qué — hace que pueda confiar en lo que el agente reporta.',
  },
];

export function HomePage() {
  const { data } = usePractices({ status: 'published' }, 1, 3);

  return (
    <div>
      <HeroCarousel slides={SLIDES} />

      <FeatureHighlights />

      <AboutIntro />

      <section className="bg-white py-16">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <span className="inline-flex items-center gap-2 text-sm font-semibold uppercase tracking-wide text-brand-600">
              <span className="h-0.5 w-8 bg-brand-500" /> Categorías
              <span className="h-0.5 w-8 bg-brand-500" />
            </span>
            <h2 className="mt-3 text-3xl font-bold text-navy-900">Categorías de prácticas</h2>
          </div>
          <div className="mt-10 grid grid-cols-1 gap-6 sm:grid-cols-2">
            {[
              {
                to: '/catalogo?type=software',
                image: categorySoftware,
                title: 'Desarrollo de software',
              },
              { to: '/catalogo?type=image', image: categoryImages, title: 'Manejo de imágenes' },
            ].map((cat) => (
              <Link
                key={cat.to}
                to={cat.to}
                className="group relative block h-64 overflow-hidden rounded-xl"
              >
                <img
                  src={cat.image}
                  alt={cat.title}
                  className="h-full w-full object-cover transition-transform duration-500 group-hover:scale-105"
                />
                <div className="absolute inset-0 bg-navy-950/50 transition-colors group-hover:bg-navy-950/60" />
                <div className="absolute bottom-5 left-5 rounded-lg bg-white px-4 py-2 shadow">
                  <span className="font-semibold text-navy-900">{cat.title}</span>
                </div>
              </Link>
            ))}
          </div>
        </div>
      </section>

      {data && data.items.length > 0 && (
        <section className="bg-ink-50 py-16">
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
            <div className="text-center">
              <span className="inline-flex items-center gap-2 text-sm font-semibold uppercase tracking-wide text-brand-600">
                <span className="h-0.5 w-8 bg-brand-500" /> Prácticas
                <span className="h-0.5 w-8 bg-brand-500" />
              </span>
              <h2 className="mt-3 text-3xl font-bold text-navy-900">Prácticas destacadas</h2>
            </div>
            <div className="mt-8 grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
              {data.items.map((practice) => (
                <PracticeCard key={practice.id} practice={practice} />
              ))}
            </div>
            <div className="mt-10 text-center">
              <Link to="/catalogo" className="btn-primary inline-flex">
                Ver todas las prácticas
              </Link>
            </div>
          </div>
        </section>
      )}

      <section className="bg-white py-16">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <span className="inline-flex items-center gap-2 text-sm font-semibold uppercase tracking-wide text-brand-600">
              <span className="h-0.5 w-8 bg-brand-500" /> Cómo funciona
              <span className="h-0.5 w-8 bg-brand-500" />
            </span>
            <h2 className="mt-3 text-3xl font-bold text-navy-900">El flujo de una práctica</h2>
          </div>
          <div className="mt-10 grid grid-cols-1 gap-8 sm:grid-cols-2 lg:grid-cols-4">
            {STEPS.map((step, i) => (
              <div key={step.title} className="relative text-center">
                <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-brand-500 text-lg font-bold text-white">
                  {i + 1}
                </div>
                <h3 className="mt-4 text-base font-semibold text-navy-900">{step.title}</h3>
                <p className="mt-2 text-sm text-ink-500">{step.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="bg-ink-50 py-16">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <span className="inline-flex items-center gap-2 text-sm font-semibold uppercase tracking-wide text-brand-600">
              <span className="h-0.5 w-8 bg-brand-500" /> Instructores
              <span className="h-0.5 w-8 bg-brand-500" />
            </span>
            <h2 className="mt-3 text-3xl font-bold text-navy-900">Quiénes la construyen</h2>
          </div>
          <div className="mt-10 grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
            {INSTRUCTORS.map((person) => (
              <div key={person.name} className="card overflow-hidden text-center">
                <img
                  src={person.photo}
                  alt={person.name}
                  className="h-56 w-full object-cover object-top"
                />
                <div className="p-4">
                  <p className="font-semibold text-navy-900">{person.name}</p>
                  <p className="mt-1 text-xs text-ink-500">{person.role}</p>
                  <div className="mt-2 flex items-center justify-center gap-1.5">
                    <img src={person.logo} alt="" className="h-4 w-auto" />
                    <p className="text-xs font-medium text-brand-600">{person.org}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="bg-navy-900 py-16">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <span className="inline-flex items-center gap-2 text-sm font-semibold uppercase tracking-wide text-brand-400">
              <span className="h-0.5 w-8 bg-brand-400" /> Testimonios
              <span className="h-0.5 w-8 bg-brand-400" />
            </span>
            <h2 className="mt-3 text-3xl font-bold text-white">Lo que dicen quienes la usan</h2>
          </div>
          <div className="mt-10 grid grid-cols-1 gap-6 sm:grid-cols-3">
            {VOICES.map((voice) => (
              <div key={voice.initials} className="rounded-xl bg-white/5 p-6">
                <span className="flex h-11 w-11 items-center justify-center rounded-full bg-brand-500 text-sm font-bold text-white">
                  {voice.initials}
                </span>
                <p className="mt-4 text-sm text-ink-200">&ldquo;{voice.quote}&rdquo;</p>
                <p className="mt-4 text-xs font-semibold uppercase tracking-wide text-brand-300">
                  {voice.role}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
}
