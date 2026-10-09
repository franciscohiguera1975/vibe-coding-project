import { usePractices } from '@/application/hooks/use-practices';
import categoryImages from '@/assets/home/category-images-practice-4.jpg';
import categorySoftware from '@/assets/home/category-software.jpg';
import heroImages from '@/assets/home/hero-images-practice.jpg';
import heroSoftware1 from '@/assets/home/hero-software-1.jpg';
import heroSoftware2 from '@/assets/home/hero-software-2.jpg';
import logoUte from '@/assets/logos/ute.png';
import logoUtpl from '@/assets/logos/utpl.png';
import instructor1 from '@/assets/team/instructor1.jpeg';
import instructor2 from '@/assets/team/instructor2.png';
import instructor3 from '@/assets/team/instructor3.png';
import instructor4 from '@/assets/team/instructor4.png';
import { AboutIntro } from '@/presentation/components/AboutIntro';
import { FeatureHighlights } from '@/presentation/components/FeatureHighlights';
import { HeroCarousel, type HeroSlide } from '@/presentation/components/HeroCarousel';
import { PracticeCard } from '@/presentation/components/PracticeCard';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';

const INSTRUCTORS = [
  {
    photo: instructor1,
    name: 'Mtr. Francisco Javier Higuera González',
    roleKey: 'homePage.instructors.instructor1Role',
    org: 'Universidad UTE',
    logo: logoUte,
  },
  {
    photo: instructor2,
    name: 'Mgs. Carlos Byron Bermeo León',
    roleKey: 'homePage.instructors.instructor2Role',
    org: 'Universidad UTPL',
    logo: logoUtpl,
  },
  {
    photo: instructor3,
    name: 'Cristian Guillermo Rivadeneira Cedeño',
    roleKey: 'homePage.instructors.instructor3Role',
    org: 'Universidad UTE',
    logo: logoUte,
  },
  {
    photo: instructor4,
    name: 'Mgs. José Francisco Silva Garcés',
    roleKey: 'homePage.instructors.instructor4Role',
    org: 'Universidad UTE',
    logo: logoUte,
  },
];

export function HomePage() {
  const { data } = usePractices({ status: 'published' }, 1, 3);
  const { t } = useTranslation();

  const SLIDES: HeroSlide[] = [
    {
      image: heroSoftware1,
      eyebrow: t('homePage.hero.slide1.eyebrow'),
      title: t('homePage.hero.slide1.title'),
      description: t('homePage.hero.slide1.description'),
      primaryCta: { label: t('homePage.hero.slide1.primaryCta'), to: '/catalogo' },
      secondaryCta: { label: t('homePage.hero.slide1.secondaryCta'), to: '/acerca' },
    },
    {
      image: heroSoftware2,
      eyebrow: t('homePage.hero.slide2.eyebrow'),
      title: t('homePage.hero.slide2.title'),
      description: t('homePage.hero.slide2.description'),
      primaryCta: { label: t('homePage.hero.slide2.primaryCta'), to: '/acerca' },
      secondaryCta: { label: t('homePage.hero.slide2.secondaryCta'), to: '/catalogo?type=software' },
    },
    {
      image: heroImages,
      eyebrow: t('homePage.hero.slide3.eyebrow'),
      title: t('homePage.hero.slide3.title'),
      description: t('homePage.hero.slide3.description'),
      primaryCta: { label: t('homePage.hero.slide3.primaryCta'), to: '/catalogo?type=image' },
      secondaryCta: { label: t('homePage.hero.slide3.secondaryCta'), to: '/acerca' },
    },
  ];

  const STEPS = [
    {
      title: t('homePage.steps.step1.title'),
      description: t('homePage.steps.step1.description'),
    },
    {
      title: t('homePage.steps.step2.title'),
      description: t('homePage.steps.step2.description'),
    },
    {
      title: t('homePage.steps.step3.title'),
      description: t('homePage.steps.step3.description'),
    },
    {
      title: t('homePage.steps.step4.title'),
      description: t('homePage.steps.step4.description'),
    },
  ];

  const VOICES = [
    {
      initials: 'DS',
      role: t('homePage.testimonials.voice1.role'),
      quote: t('homePage.testimonials.voice1.quote'),
    },
    {
      initials: 'MI',
      role: t('homePage.testimonials.voice2.role'),
      quote: t('homePage.testimonials.voice2.quote'),
    },
    {
      initials: 'DC',
      role: t('homePage.testimonials.voice3.role'),
      quote: t('homePage.testimonials.voice3.quote'),
    },
  ];

  const CATEGORIES = [
    {
      to: '/catalogo?type=software',
      image: categorySoftware,
      title: t('homePage.categories.software'),
    },
    { to: '/catalogo?type=image', image: categoryImages, title: t('homePage.categories.image') },
  ];

  return (
    <div>
      <HeroCarousel slides={SLIDES} />

      <FeatureHighlights />

      <AboutIntro />

      <section className="bg-white py-16">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <span className="inline-flex items-center gap-2 text-sm font-semibold uppercase tracking-wide text-brand-600">
              <span className="h-0.5 w-8 bg-brand-500" /> {t('homePage.categories.eyebrow')}
              <span className="h-0.5 w-8 bg-brand-500" />
            </span>
            <h2 className="mt-3 text-3xl font-bold text-navy-900">
              {t('homePage.categories.title')}
            </h2>
          </div>
          <div className="mt-10 grid grid-cols-1 gap-6 sm:grid-cols-2">
            {CATEGORIES.map((cat) => (
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
                <span className="h-0.5 w-8 bg-brand-500" /> {t('homePage.featured.eyebrow')}
                <span className="h-0.5 w-8 bg-brand-500" />
              </span>
              <h2 className="mt-3 text-3xl font-bold text-navy-900">
                {t('homePage.featured.title')}
              </h2>
            </div>
            <div className="mt-8 grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
              {data.items.map((practice) => (
                <PracticeCard key={practice.id} practice={practice} />
              ))}
            </div>
            <div className="mt-10 text-center">
              <Link to="/catalogo" className="btn-primary inline-flex">
                {t('homePage.featured.viewAll')}
              </Link>
            </div>
          </div>
        </section>
      )}

      <section className="bg-white py-16">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <span className="inline-flex items-center gap-2 text-sm font-semibold uppercase tracking-wide text-brand-600">
              <span className="h-0.5 w-8 bg-brand-500" /> {t('homePage.steps.eyebrow')}
              <span className="h-0.5 w-8 bg-brand-500" />
            </span>
            <h2 className="mt-3 text-3xl font-bold text-navy-900">{t('homePage.steps.title')}</h2>
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
              <span className="h-0.5 w-8 bg-brand-500" /> {t('homePage.instructors.eyebrow')}
              <span className="h-0.5 w-8 bg-brand-500" />
            </span>
            <h2 className="mt-3 text-3xl font-bold text-navy-900">
              {t('homePage.instructors.title')}
            </h2>
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
                  <p className="mt-1 text-xs text-ink-500">{t(person.roleKey)}</p>
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
              <span className="h-0.5 w-8 bg-brand-400" /> {t('homePage.testimonials.eyebrow')}
              <span className="h-0.5 w-8 bg-brand-400" />
            </span>
            <h2 className="mt-3 text-3xl font-bold text-white">
              {t('homePage.testimonials.title')}
            </h2>
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
