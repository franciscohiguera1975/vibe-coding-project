import {
  useCreatePractice,
  usePractices,
  usePublishPractice,
} from '@/application/hooks/use-practices';
import { FormEvent, useState } from 'react';

const STATUS_COLOR: Record<string, string> = {
  draft: 'bg-ink-100 text-ink-600',
  published: 'bg-emerald-50 text-emerald-700',
  archived: 'bg-amber-50 text-amber-700',
};

export function PracticesAdminPage() {
  const [page, setPage] = useState(1);
  const { data, isLoading } = usePractices({}, page, 20);
  const createPractice = useCreatePractice();
  const publishPractice = usePublishPractice();
  const [showForm, setShowForm] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [form, setForm] = useState({
    title: '',
    type: 'software',
    instructions: '',
    content: '{}',
    evaluation: '{}',
  });

  async function handleCreate(event: FormEvent) {
    event.preventDefault();
    setError(null);
    try {
      const content = JSON.parse(form.content || '{}');
      const evaluation = JSON.parse(form.evaluation || '{}');
      await createPractice.mutateAsync({
        title: form.title,
        type: form.type,
        instructions: form.instructions,
        content,
        evaluation,
      });
      setShowForm(false);
      setForm({ title: '', type: 'software', instructions: '', content: '{}', evaluation: '{}' });
    } catch {
      setError('Revise el formulario: el contenido y la evaluación deben ser JSON válido.');
    }
  }

  return (
    <div>
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold text-ink-900">Prácticas</h1>
        <button className="btn-primary" onClick={() => setShowForm((v) => !v)}>
          {showForm ? 'Cancelar' : 'Nueva práctica'}
        </button>
      </div>

      {showForm && (
        <form onSubmit={handleCreate} className="card mt-4 space-y-3 p-5">
          <div>
            <label className="label">Título</label>
            <input
              required
              className="input"
              value={form.title}
              onChange={(e) => setForm((f) => ({ ...f, title: e.target.value }))}
            />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="label">Tipo</label>
              <select
                className="input"
                value={form.type}
                onChange={(e) => setForm((f) => ({ ...f, type: e.target.value }))}
              >
                <option value="software">software</option>
                <option value="image">image</option>
              </select>
            </div>
          </div>
          <div>
            <label className="label">Instrucciones</label>
            <textarea
              required
              className="input"
              rows={3}
              value={form.instructions}
              onChange={(e) => setForm((f) => ({ ...f, instructions: e.target.value }))}
            />
          </div>
          <div>
            <label className="label">Contenido (JSON)</label>
            <textarea
              className="input font-mono text-xs"
              rows={4}
              value={form.content}
              onChange={(e) => setForm((f) => ({ ...f, content: e.target.value }))}
            />
          </div>
          <div>
            <label className="label">Evaluación (JSON)</label>
            <textarea
              className="input font-mono text-xs"
              rows={4}
              value={form.evaluation}
              onChange={(e) => setForm((f) => ({ ...f, evaluation: e.target.value }))}
            />
          </div>
          {error && <p className="text-sm text-rose-600">{error}</p>}
          <button type="submit" className="btn-primary" disabled={createPractice.isPending}>
            {createPractice.isPending ? 'Creando...' : 'Crear práctica'}
          </button>
        </form>
      )}

      <div className="mt-6 overflow-x-auto">
        {isLoading && <p className="text-sm text-ink-500">Cargando...</p>}
        <table className="w-full min-w-[640px] text-left text-sm">
          <thead>
            <tr className="border-b border-ink-100 text-ink-500">
              <th className="py-2">Título</th>
              <th className="py-2">Tipo</th>
              <th className="py-2">Estado</th>
              <th className="py-2"></th>
            </tr>
          </thead>
          <tbody>
            {data?.items.map((practice) => (
              <tr key={practice.id} className="border-b border-ink-50">
                <td className="py-2 font-medium text-ink-900">{practice.title}</td>
                <td className="py-2 text-ink-500">{practice.type}</td>
                <td className="py-2">
                  <span
                    className={`badge ${STATUS_COLOR[practice.status] ?? 'bg-ink-100 text-ink-600'}`}
                  >
                    {practice.status}
                  </span>
                </td>
                <td className="py-2 text-right">
                  {practice.status === 'draft' && (
                    <button
                      className="btn-secondary"
                      disabled={publishPractice.isPending}
                      onClick={() => publishPractice.mutate(practice.id)}
                    >
                      Publicar
                    </button>
                  )}
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
