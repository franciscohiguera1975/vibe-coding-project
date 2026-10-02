import { PracticeWorkspace } from '@/presentation/practices/PracticeWorkspace';
import { useParams } from 'react-router-dom';

/** Vista sin header/footer/navegación pensada para incrustarse en un <iframe> de
 * Moodle (ver docs/moodle-integration.md). Se monta fuera de PublicLayout en el
 * router para no traer la barra de navegación ni el pie de página. */
export function PracticeEmbedPage() {
  const { slug } = useParams<{ slug: string }>();

  return (
    <div className="mx-auto max-w-3xl px-4 py-6">
      <PracticeWorkspace slug={slug} embedded />
    </div>
  );
}
