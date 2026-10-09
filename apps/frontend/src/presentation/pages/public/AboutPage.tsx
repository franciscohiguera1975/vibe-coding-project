import { AboutIntro } from '@/presentation/components/AboutIntro';
import { FeatureHighlights } from '@/presentation/components/FeatureHighlights';
import { PageHeader } from '@/presentation/components/PageHeader';
import { useTranslation } from 'react-i18next';

export function AboutPage() {
  const { t } = useTranslation();

  const STEPS = [
    {
      title: t('aboutPage.steps.step1.title'),
      description: t('aboutPage.steps.step1.description'),
    },
    {
      title: t('aboutPage.steps.step2.title'),
      description: t('aboutPage.steps.step2.description'),
    },
    {
      title: t('aboutPage.steps.step3.title'),
      description: t('aboutPage.steps.step3.description'),
    },
    {
      title: t('aboutPage.steps.step4.title'),
      description: t('aboutPage.steps.step4.description'),
    },
    {
      title: t('aboutPage.steps.step5.title'),
      description: t('aboutPage.steps.step5.description'),
    },
  ];

  return (
    <div>
      <PageHeader
        title={t('aboutPage.pageTitle')}
        breadcrumbs={[
          { label: t('aboutPage.breadcrumbs.home'), to: '/' },
          { label: t('aboutPage.breadcrumbs.about') },
        ]}
      />

      <FeatureHighlights />
      <AboutIntro showCta={false} />

      <div className="mx-auto max-w-4xl px-4 py-16 sm:px-6 lg:px-8">
        <span className="inline-flex items-center gap-2 text-sm font-semibold uppercase tracking-wide text-brand-600">
          <span className="h-0.5 w-8 bg-brand-500" /> {t('aboutPage.steps.eyebrow')}
        </span>
        <h2 className="mt-3 text-2xl font-bold text-navy-900">{t('aboutPage.steps.title')}</h2>
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
