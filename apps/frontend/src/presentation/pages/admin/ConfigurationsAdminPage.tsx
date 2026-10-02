import { useConfigurations, useUpdateConfiguration } from '@/application/hooks/use-admin';
import { useState } from 'react';

export function ConfigurationsAdminPage() {
  const { data: configurations, isLoading } = useConfigurations();
  const updateConfiguration = useUpdateConfiguration();
  const [drafts, setDrafts] = useState<Record<string, string>>({});
  const [errors, setErrors] = useState<Record<string, string>>({});

  function draftFor(key: string, fallback: Record<string, unknown>): string {
    return drafts[key] ?? JSON.stringify(fallback, null, 2);
  }

  async function handleSave(key: string, description: string) {
    setErrors((e) => ({ ...e, [key]: '' }));
    try {
      const value = JSON.parse(draftFor(key, {}));
      await updateConfiguration.mutateAsync({ key, value, description });
    } catch {
      setErrors((e) => ({ ...e, [key]: 'JSON inválido' }));
    }
  }

  return (
    <div>
      <h1 className="text-2xl font-semibold text-ink-900">Configuraciones</h1>
      <p className="mt-1 text-sm text-ink-500">Valores clave/valor usados por la plataforma.</p>

      <div className="mt-6 space-y-4">
        {isLoading && <p className="text-sm text-ink-500">Cargando...</p>}
        {configurations?.map((config) => (
          <div key={config.key} className="card p-5">
            <div className="flex items-center justify-between">
              <h2 className="font-mono text-sm font-semibold text-ink-900">{config.key}</h2>
            </div>
            <p className="mt-1 text-xs text-ink-400">{config.description}</p>
            <textarea
              className="input mt-2 font-mono text-xs"
              rows={3}
              value={draftFor(config.key, config.value)}
              onChange={(e) => setDrafts((d) => ({ ...d, [config.key]: e.target.value }))}
            />
            {errors[config.key] && <p className="text-sm text-rose-600">{errors[config.key]}</p>}
            <button
              className="btn-secondary mt-2"
              onClick={() => handleSave(config.key, config.description)}
              disabled={updateConfiguration.isPending}
            >
              Guardar
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
