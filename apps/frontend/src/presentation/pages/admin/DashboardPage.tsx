import { useAuth } from '@/application/hooks/auth-context';
import { Link } from 'react-router-dom';

const CARDS = [
  {
    to: '/admin/practicas',
    title: 'Prácticas',
    description: 'Crear, editar y publicar prácticas del catálogo.',
  },
  {
    to: '/admin/categorias',
    title: 'Categorías',
    description: 'Organizar el catálogo por categorías.',
  },
  { to: '/admin/usuarios', title: 'Usuarios', description: 'Crear usuarios y asignar roles.' },
  {
    to: '/admin/roles',
    title: 'Roles y permisos',
    description: 'Revisar roles y asignar permisos.',
  },
  {
    to: '/admin/configuraciones',
    title: 'Configuraciones',
    description: 'Ajustar parámetros de la plataforma.',
  },
  {
    to: '/admin/auditoria',
    title: 'Auditoría',
    description: 'Ver el registro de acciones administrativas.',
  },
];

export function DashboardPage() {
  const { user } = useAuth();

  return (
    <div>
      <h1 className="text-2xl font-semibold text-ink-900">Panel de administración</h1>
      <p className="mt-1 text-sm text-ink-500">Bienvenido, {user?.fullName}.</p>

      <div className="mt-8 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {CARDS.map((card) => (
          <Link key={card.to} to={card.to} className="card p-5 transition-shadow hover:shadow-md">
            <h2 className="font-semibold text-ink-900">{card.title}</h2>
            <p className="mt-1 text-sm text-ink-500">{card.description}</p>
          </Link>
        ))}
      </div>
    </div>
  );
}
