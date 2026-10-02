import defaultBanner from '@/assets/home/hero-software-2.jpg';
import { Fragment } from 'react';
import { Link } from 'react-router-dom';

interface Breadcrumb {
  label: string;
  to?: string;
}

interface PageHeaderProps {
  title: string;
  breadcrumbs: Breadcrumb[];
  image?: string;
}

/** Banner de cabecera reutilizable para páginas internas (no para el home, que
 * usa HeroCarousel, ni para la vista embebida de prácticas, que debe quedar sin
 * chrome para Moodle — ver PracticeWorkspace). */
export function PageHeader({ title, breadcrumbs, image = defaultBanner }: PageHeaderProps) {
  return (
    <div
      className="relative flex h-56 items-center justify-center bg-cover bg-center sm:h-64"
      style={{ backgroundImage: `url(${image})` }}
    >
      <div className="absolute inset-0 bg-navy-950/70" />
      <div className="relative text-center">
        <h1 className="text-3xl font-bold text-white sm:text-4xl">{title}</h1>
        <nav className="mt-3 flex items-center justify-center gap-2 text-sm text-ink-200">
          {breadcrumbs.map((crumb, i) => (
            <Fragment key={crumb.label}>
              {i > 0 && <span className="text-ink-400">/</span>}
              {crumb.to ? (
                <Link to={crumb.to} className="hover:text-white">
                  {crumb.label}
                </Link>
              ) : (
                <span className="text-white">{crumb.label}</span>
              )}
            </Fragment>
          ))}
        </nav>
      </div>
    </div>
  );
}
