import { useAskTutor } from '@/application/hooks/use-ai';
import { FormEvent, useState } from 'react';

export function AskTutorPanel({ practiceSlug }: { practiceSlug: string }) {
  const askTutor = useAskTutor();
  const [message, setMessage] = useState('');
  const [response, setResponse] = useState<string | null>(null);
  const [open, setOpen] = useState(false);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    if (!message.trim()) return;
    const result = await askTutor.mutateAsync({ slug: practiceSlug, message });
    setResponse(result.response);
  }

  if (!open) {
    return (
      <button className="btn-secondary" onClick={() => setOpen(true)}>
        🎓 Preguntar al tutor de IA
      </button>
    );
  }

  return (
    <div className="card p-4">
      <h3 className="text-sm font-semibold text-ink-900">Tutor de IA</h3>
      <p className="mt-1 text-xs text-ink-500">
        El tutor conoce la práctica y su progreso; no revelará la respuesta exacta.
      </p>
      <form onSubmit={handleSubmit} className="mt-3 flex gap-2">
        <input
          className="input"
          placeholder="Escriba su pregunta..."
          value={message}
          onChange={(e) => setMessage(e.target.value)}
        />
        <button type="submit" className="btn-primary shrink-0" disabled={askTutor.isPending}>
          {askTutor.isPending ? 'Pensando...' : 'Preguntar'}
        </button>
      </form>
      {response && (
        <p className="mt-3 rounded-lg bg-brand-50 p-3 text-sm text-brand-900">{response}</p>
      )}
    </div>
  );
}
