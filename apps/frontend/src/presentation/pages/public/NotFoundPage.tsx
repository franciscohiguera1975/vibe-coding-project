import { Link } from 'react-router-dom';

export function NotFoundPage() {
  return (
    <div className="mx-auto flex min-h-[60vh] max-w-xl flex-col items-center justify-center px-4 text-center">
      <p className="text-sm font-semibold text-brand-600">404</p>
      <h1 className="mt-2 text-2xl font-semibold text-ink-900">Página no encontrada</h1>
      <p className="mt-2 text-sm text-ink-500">El contenido que busca no existe o fue movido.</p>
      <Link to="/" className="btn-primary mt-6">
        Volver al inicio
      </Link>
    </div>
  );
}
