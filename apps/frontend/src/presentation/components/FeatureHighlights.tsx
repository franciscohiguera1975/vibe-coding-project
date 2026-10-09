import { useTranslation } from 'react-i18next';

const ICONS = [
  (
    <path
      key="vibe-coding"
      strokeLinecap="round"
      strokeLinejoin="round"
      d="M9 8l-4 4 4 4m6-8l4 4-4 4M13 4l-2 16"
    />
  ),
  (
    <>
      <rect x="3" y="4" width="18" height="16" rx="2" />
      <circle cx="9" cy="10" r="2" />
      <path strokeLinecap="round" strokeLinejoin="round" d="M21 16l-5.5-5.5L7 19" />
    </>
  ),
  (
    <>
      <path strokeLinecap="round" strokeLinejoin="round" d="M12 3v2m0 14v2M5 12H3m18 0h-2" />
      <rect x="6" y="6" width="12" height="12" rx="3" />
    </>
  ),
  (
    <>
      <rect x="3" y="4" width="18" height="12" rx="2" />
      <path strokeLinecap="round" strokeLinejoin="round" d="M8 20h8M12 16v4" />
    </>
  ),
];

/** Fila de 4 íconos con las características principales. Usada tanto en el
 * home como en "La plataforma" (AboutPage) para mantener el mismo patrón de
 * la referencia visual en ambas páginas. */
export function FeatureHighlights() {
  const { t } = useTranslation();

  const HIGHLIGHTS = [
    {
      title: t('featureHighlights.items.vibeCoding.title'),
      description: t('featureHighlights.items.vibeCoding.description'),
      icon: ICONS[0],
    },
    {
      title: t('featureHighlights.items.imageHandling.title'),
      description: t('featureHighlights.items.imageHandling.description'),
      icon: ICONS[1],
    },
    {
      title: t('featureHighlights.items.aiTutor.title'),
      description: t('featureHighlights.items.aiTutor.description'),
      icon: ICONS[2],
    },
    {
      title: t('featureHighlights.items.moodleEmbed.title'),
      description: t('featureHighlights.items.moodleEmbed.description'),
      icon: ICONS[3],
    },
  ];

  return (
    <section className="bg-white py-14">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
          {HIGHLIGHTS.map((item) => (
            <div
              key={item.title}
              className="rounded-xl bg-brand-50/60 p-6 text-center transition-shadow hover:shadow-md"
            >
              <svg
                viewBox="0 0 24 24"
                className="mx-auto h-10 w-10 text-brand-600"
                fill="none"
                stroke="currentColor"
                strokeWidth={1.5}
              >
                {item.icon}
              </svg>
              <h3 className="mt-4 text-base font-semibold text-navy-900">{item.title}</h3>
              <p className="mt-2 text-sm text-ink-500">{item.description}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
