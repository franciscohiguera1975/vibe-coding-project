import { usePractice } from '@/application/hooks/use-practices';
import { PageHeader } from '@/presentation/components/PageHeader';
import { getPracticeTypeCover } from '@/presentation/practices/type-images';
import { PracticeWorkspace } from '@/presentation/practices/PracticeWorkspace';
import { useParams } from 'react-router-dom';

export function PracticeDetailPage() {
  const { slug } = useParams<{ slug: string }>();
  const { data: practice } = usePractice(slug);

  return (
    <div>
      <PageHeader
        title={practice?.title ?? 'Práctica'}
        image={practice ? getPracticeTypeCover(practice.type, practice.id) : undefined}
        breadcrumbs={[
          { label: 'Inicio', to: '/' },
          { label: 'Catálogo', to: '/catalogo' },
          { label: practice?.title ?? 'Práctica' },
        ]}
      />
      <div className="mx-auto max-w-4xl px-4 py-12 sm:px-6 lg:px-8">
        <PracticeWorkspace slug={slug} hideHeading />
      </div>
    </div>
  );
}
