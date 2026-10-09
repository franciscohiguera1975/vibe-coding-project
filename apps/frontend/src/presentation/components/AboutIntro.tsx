import aboutImage from '@/assets/home/about-learning-to-code.jpg';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';

interface AboutIntroProps {
  /** false en la propia página "La plataforma" — no tiene sentido enlazar
   * "Leer más" hacia la misma página que ya se está viendo. */
  showCta?: boolean;
}

/** Bloque foto + texto de "Acerca de". Compartido entre el home y AboutPage
 * para mantener el mismo patrón visual en ambas páginas. */
export function AboutIntro({ showCta = true }: AboutIntroProps) {
  const { t } = useTranslation();

  const BULLETS = [
    t('aboutIntro.bullets.reusablePractices'),
    t('aboutIntro.bullets.explicitEvaluation'),
    t('aboutIntro.bullets.aiTutor'),
    t('aboutIntro.bullets.embeddable'),
  ];

  return (
    <section className="bg-ink-50 py-16">
      <div className="mx-auto grid max-w-7xl grid-cols-1 gap-10 px-4 sm:px-6 lg:grid-cols-2 lg:px-8">
        <img
          src={aboutImage}
          alt={t('aboutIntro.imageAlt')}
          className="h-full w-full rounded-xl object-cover shadow-sm"
        />
        <div>
          <span className="inline-flex items-center gap-2 text-sm font-semibold uppercase tracking-wide text-brand-600">
            <span className="h-0.5 w-8 bg-brand-500" /> {t('aboutIntro.eyebrow')}
          </span>
          <h2 className="mt-3 text-3xl font-bold text-navy-900">{t('aboutIntro.title')}</h2>
          <p className="mt-4 text-ink-600">{t('aboutIntro.description')}</p>
          <div className="mt-6 grid grid-cols-1 gap-x-8 gap-y-2 sm:grid-cols-2">
            {BULLETS.map((item) => (
              <p key={item} className="flex items-center gap-2 text-sm text-ink-700">
                <svg
                  viewBox="0 0 24 24"
                  className="h-4 w-4 flex-shrink-0 text-brand-500"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth={2}
                >
                  <path strokeLinecap="round" strokeLinejoin="round" d="M5 12h14M13 6l6 6-6 6" />
                </svg>
                {item}
              </p>
            ))}
          </div>
          {showCta && (
            <Link to="/acerca" className="btn-primary mt-8 inline-flex">
              {t('aboutIntro.readMore')}
            </Link>
          )}
        </div>
      </div>
    </section>
  );
}
