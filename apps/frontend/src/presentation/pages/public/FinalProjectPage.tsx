import { PageHeader } from '@/presentation/components/PageHeader';

const VIDEOS = [
  {
    lang: 'Español',
    src: '/videos/proyecto-final-es.mp4',
    duration: '4:32',
  },
  {
    lang: 'English',
    src: '/videos/proyecto-final-en.mp4',
    duration: '4:44',
  },
];

export function FinalProjectPage() {
  return (
    <div>
      <PageHeader
        title="Proyecto final · Vibe Coding CEDIA 2026"
        breadcrumbs={[{ label: 'Inicio', to: '/' }, { label: 'Presentación' }]}
      />

      <div className="mx-auto max-w-5xl px-4 py-16 sm:px-6 lg:px-8">
        <div className="text-center">
          <span className="inline-flex items-center gap-2 text-sm font-semibold uppercase tracking-wide text-brand-600">
            <span className="h-0.5 w-8 bg-brand-500" /> Presentación
            <span className="h-0.5 w-8 bg-brand-500" />
          </span>
          <h2 className="mt-3 text-3xl font-bold text-navy-900">
            Vibe Coding Platform, presentada por sus autores
          </h2>
          <p className="mx-auto mt-4 max-w-2xl text-ink-500">
            Francisco Javier Higuera González (Universidad UTE) y Carlos Byron Bermeo León
            (Universidad UTPL) presentan la plataforma construida durante el curso Vibe Coding
            CEDIA 2026, con narración generada con voz de IA (ElevenLabs) y revisada por los
            autores.
          </p>
        </div>

        <div className="mt-12 grid grid-cols-1 gap-10 lg:grid-cols-2">
          {VIDEOS.map((video) => (
            <div key={video.lang} className="card overflow-hidden">
              <video controls preload="none" className="aspect-video w-full bg-navy-950">
                <source src={video.src} type="video/mp4" />
              </video>
              <div className="flex items-center justify-between p-4">
                <span className="font-semibold text-navy-900">Video · {video.lang}</span>
                <span className="text-sm text-ink-500">{video.duration}</span>
              </div>
            </div>
          ))}
        </div>

        <div className="mt-12 text-center">
          <a
            href="https://github.com/franciscohiguera1975/vibe-coding-proyecto-final"
            target="_blank"
            rel="noreferrer"
            className="text-sm font-semibold text-brand-600 hover:text-brand-700"
          >
            Repositorio del proyecto final (presentaciones y nota metodológica) →
          </a>
        </div>
      </div>
    </div>
  );
}
