import { useCategories, useCreateCategory } from '@/application/hooks/use-admin';
import { FormEvent, useState } from 'react';

export function CategoriesAdminPage() {
  const { data: categories, isLoading } = useCategories();
  const createCategory = useCreateCategory();
  const [name, setName] = useState('');
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setError(null);
    try {
      await createCategory.mutateAsync(name);
      setName('');
    } catch {
      setError('No se pudo crear la categoría (¿el nombre ya existe?).');
    }
  }

  return (
    <div>
      <h1 className="text-2xl font-semibold text-ink-900">Categorías</h1>

      <form onSubmit={handleSubmit} className="card mt-4 flex items-end gap-3 p-5">
        <div className="flex-1">
          <label className="label">Nombre de la categoría</label>
          <input
            required
            className="input"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="p. ej. Inteligencia Artificial"
          />
        </div>
        <button type="submit" className="btn-primary" disabled={createCategory.isPending}>
          Crear
        </button>
      </form>
      {error && <p className="mt-2 text-sm text-rose-600">{error}</p>}

      <div className="mt-6 grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
        {isLoading && <p className="text-sm text-ink-500">Cargando...</p>}
        {categories?.map((category) => (
          <div key={category.id} className="card p-4">
            <p className="font-medium text-ink-900">{category.name}</p>
            <p className="text-xs text-ink-400">{category.slug}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
