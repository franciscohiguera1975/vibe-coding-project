import type { PracticeRunnerProps } from '@/presentation/practices/types';

export function UnknownPracticeType({ practice }: PracticeRunnerProps) {
  return (
    <div className="card p-5 text-sm text-ink-500">
      No hay un contenido interactivo registrado para el tipo de práctica «{practice.type}». Un
      administrador puede agregar un nuevo componente en el registro de tipos sin modificar el resto
      de la plataforma.
    </div>
  );
}
