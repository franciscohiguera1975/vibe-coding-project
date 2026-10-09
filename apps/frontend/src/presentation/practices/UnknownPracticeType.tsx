import type { PracticeRunnerProps } from '@/presentation/practices/types';
import { useTranslation } from 'react-i18next';

export function UnknownPracticeType({ practice }: PracticeRunnerProps) {
  const { t } = useTranslation();

  return (
    <div className="card p-5 text-sm text-ink-500">
      {t('unknownPracticeType.message', { type: practice.type })}
    </div>
  );
}
