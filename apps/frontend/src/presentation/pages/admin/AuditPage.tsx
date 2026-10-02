import { useAuditLogs } from '@/application/hooks/use-admin';
import { useState } from 'react';

export function AuditPage() {
  const [page, setPage] = useState(1);
  const { data, isLoading } = useAuditLogs(page);

  return (
    <div>
      <h1 className="text-2xl font-semibold text-ink-900">Auditoría</h1>
      <p className="mt-1 text-sm text-ink-500">Registro de acciones administrativas sensibles.</p>

      <div className="mt-6 overflow-x-auto">
        {isLoading && <p className="text-sm text-ink-500">Cargando...</p>}
        <table className="w-full min-w-[720px] text-left text-sm">
          <thead>
            <tr className="border-b border-ink-100 text-ink-500">
              <th className="py-2">Fecha</th>
              <th className="py-2">Acción</th>
              <th className="py-2">Entidad</th>
              <th className="py-2">Detalle</th>
            </tr>
          </thead>
          <tbody>
            {data?.items.map((log) => (
              <tr key={log.id} className="border-b border-ink-50 align-top">
                <td className="py-2 whitespace-nowrap text-ink-500">
                  {new Date(log.createdAt).toLocaleString()}
                </td>
                <td className="py-2 font-medium text-ink-900">{log.action}</td>
                <td className="py-2 text-ink-500">
                  {log.entityType}
                  {log.entityId ? ` #${log.entityId.slice(0, 8)}` : ''}
                </td>
                <td className="py-2 font-mono text-xs text-ink-400">
                  {JSON.stringify(log.metadata)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {data && data.totalPages > 1 && (
        <div className="mt-4 flex items-center justify-center gap-3">
          <button
            className="btn-secondary"
            disabled={page <= 1}
            onClick={() => setPage((p) => p - 1)}
          >
            Anterior
          </button>
          <span className="text-sm text-ink-500">
            Página {data.page} de {data.totalPages}
          </span>
          <button
            className="btn-secondary"
            disabled={page >= data.totalPages}
            onClick={() => setPage((p) => p + 1)}
          >
            Siguiente
          </button>
        </div>
      )}
    </div>
  );
}
