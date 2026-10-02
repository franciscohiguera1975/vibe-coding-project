import { Link } from 'react-router-dom';

export function Footer() {
  return (
    <footer className="border-t border-ink-100 bg-white">
      <div className="mx-auto max-w-7xl px-4 py-10 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 gap-8 sm:grid-cols-3">
          <div>
            <span className="text-base font-semibold text-ink-900">Vibe Coding Platform</span>
            <p className="mt-2 max-w-xs text-sm text-ink-500">
              Enseñanza práctica de desarrollo de software y manejo de imágenes con IA e IA
              agéntica.
            </p>
          </div>
          <div>
            <h3 className="text-sm font-semibold text-ink-900">Explorar</h3>
            <ul className="mt-3 space-y-2 text-sm text-ink-500">
              <li>
                <Link to="/catalogo" className="hover:text-brand-600">
                  Catálogo de prácticas
                </Link>
              </li>
              <li>
                <Link to="/acerca" className="hover:text-brand-600">
                  Acerca de la plataforma
                </Link>
              </li>
            </ul>
          </div>
          <div>
            <h3 className="text-sm font-semibold text-ink-900">Integración</h3>
            <ul className="mt-3 space-y-2 text-sm text-ink-500">
              <li>Embebido para Moodle, D2L y Canvas</li>
              <li>API documentada (OpenAPI/Swagger)</li>
            </ul>
          </div>
        </div>
        <p className="mt-8 border-t border-ink-100 pt-6 text-xs text-ink-400">
          © {new Date().getFullYear()} Vibe Coding Platform · Proyecto educativo CEDIA · UTE
        </p>
      </div>
    </footer>
  );
}
