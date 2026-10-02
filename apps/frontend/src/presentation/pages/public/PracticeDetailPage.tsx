import { PracticeWorkspace } from '@/presentation/practices/PracticeWorkspace';
import { useParams } from 'react-router-dom';

export function PracticeDetailPage() {
  const { slug } = useParams<{ slug: string }>();

  return (
    <div className="mx-auto max-w-4xl px-4 py-12 sm:px-6 lg:px-8">
      <PracticeWorkspace slug={slug} />
    </div>
  );
}
