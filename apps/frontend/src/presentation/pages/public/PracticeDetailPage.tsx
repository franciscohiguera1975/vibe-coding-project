import { usePractice } from '@/application/hooks/use-practices';
import { PageHeader } from '@/presentation/components/PageHeader';
import { getPracticeTypeCover } from '@/presentation/practices/type-images';
import { PracticeWorkspace } from '@/presentation/practices/PracticeWorkspace';
import { useTranslation } from 'react-i18next';
import { useParams } from 'react-router-dom';

export function PracticeDetailPage() {
  const { t } = useTranslation();
  const { slug } = useParams<{ slug: string }>();
  const { data: practice } = usePractice(slug);
  const fallbackTitle = t('practiceDetailPage.fallbackTitle');

  return (
    <div>
      <PageHeader
        title={practice?.title ?? fallbackTitle}
        image={practice ? getPracticeTypeCover(practice.type, practice.id) : undefined}
        breadcrumbs={[
          { label: t('practiceDetailPage.breadcrumbs.home'), to: '/' },
          { label: t('practiceDetailPage.breadcrumbs.catalog'), to: '/catalogo' },
          { label: practice?.title ?? fallbackTitle },
        ]}
      />
      <div className="mx-auto max-w-4xl px-4 py-12 sm:px-6 lg:px-8">
        <PracticeWorkspace slug={slug} hideHeading />
      </div>
    </div>
  );
}
