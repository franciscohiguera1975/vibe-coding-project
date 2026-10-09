import { useTranslation } from 'react-i18next';

const LANGUAGES = [
  { code: 'es', flag: '🇪🇸', label: 'Español' },
  { code: 'en', flag: '🇬🇧', label: 'English' },
  { code: 'pt', flag: '🇧🇷', label: 'Português' },
  { code: 'fr', flag: '🇫🇷', label: 'Français' },
] as const;

export function LanguageSwitcher() {
  const { t, i18n } = useTranslation();
  const current = LANGUAGES.find((l) => l.code === i18n.resolvedLanguage) ?? LANGUAGES[0];

  return (
    <div className="relative inline-flex items-center">
      <span aria-hidden className="pointer-events-none absolute left-2 text-base">
        {current.flag}
      </span>
      <select
        aria-label={t('language.label')}
        value={current.code}
        onChange={(e) => i18n.changeLanguage(e.target.value)}
        className="cursor-pointer appearance-none rounded-md border border-ink-100 bg-white py-1.5 pl-8 pr-6 text-sm font-semibold text-navy-700 transition-colors hover:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-500"
      >
        {LANGUAGES.map((lang) => (
          <option key={lang.code} value={lang.code}>
            {lang.label}
          </option>
        ))}
      </select>
    </div>
  );
}
