import { useChatNormativa } from '@/application/hooks/use-rag';
import type { CitationRef } from '@/domain/entities/rag';
import { PageHeader } from '@/presentation/components/PageHeader';
import { useState } from 'react';
import { useTranslation } from 'react-i18next';

interface ChatMessage {
  role: 'user' | 'assistant';
  text: string;
  citations?: CitationRef[];
}

export function NormativaChatPage() {
  const { t } = useTranslation();
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [question, setQuestion] = useState('');
  const chat = useChatNormativa();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const trimmed = question.trim();
    if (!trimmed || chat.isPending) return;

    setMessages((prev) => [...prev, { role: 'user', text: trimmed }]);
    setQuestion('');

    chat.mutate(trimmed, {
      onSuccess: (result) => {
        setMessages((prev) => [
          ...prev,
          { role: 'assistant', text: result.answer, citations: result.citations },
        ]);
      },
      onError: () => {
        setMessages((prev) => [
          ...prev,
          { role: 'assistant', text: t('normativaChatPage.error') },
        ]);
      },
    });
  };

  return (
    <div>
      <PageHeader
        title={t('normativaChatPage.pageTitle')}
        breadcrumbs={[
          { label: t('normativaChatPage.breadcrumbs.home'), to: '/' },
          { label: t('normativaChatPage.breadcrumbs.current') },
        ]}
      />

      <div className="mx-auto max-w-3xl px-4 py-12 sm:px-6 lg:px-8">
        <p className="text-ink-500">{t('normativaChatPage.description')}</p>

        <div className="mt-8 flex min-h-[24rem] flex-col gap-4 rounded-lg border border-ink-100 bg-white p-4 sm:p-6">
          {messages.length === 0 && (
            <p className="m-auto text-sm text-ink-400">{t('normativaChatPage.empty')}</p>
          )}

          {messages.map((message, i) => (
            <div
              key={i}
              className={`max-w-[85%] rounded-lg px-4 py-3 text-sm ${
                message.role === 'user'
                  ? 'ml-auto bg-brand-500 text-white'
                  : 'mr-auto bg-navy-50 text-navy-900'
              }`}
            >
              <p className="whitespace-pre-wrap">{message.text}</p>
              {message.citations && message.citations.length > 0 && (
                <div className="mt-2 flex flex-wrap gap-2 border-t border-navy-100 pt-2">
                  <span className="text-xs font-semibold uppercase tracking-wide text-ink-400">
                    {t('normativaChatPage.citationsLabel')}
                  </span>
                  {message.citations.map((c, j) => (
                    <span
                      key={j}
                      className="rounded-full bg-white px-2.5 py-0.5 text-xs font-medium text-brand-700 ring-1 ring-brand-200"
                      title={c.sourceDocument}
                    >
                      {c.articleLabel}
                    </span>
                  ))}
                </div>
              )}
            </div>
          ))}

          {chat.isPending && (
            <div className="mr-auto max-w-[85%] rounded-lg bg-navy-50 px-4 py-3 text-sm text-ink-500">
              {t('normativaChatPage.thinking')}
            </div>
          )}
        </div>

        <form onSubmit={handleSubmit} className="mt-4 flex gap-2">
          <input
            type="text"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder={t('normativaChatPage.inputPlaceholder')}
            className="flex-1 rounded-md border border-ink-200 px-4 py-2.5 text-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
            disabled={chat.isPending}
          />
          <button
            type="submit"
            className="btn-primary"
            disabled={chat.isPending || !question.trim()}
          >
            {t('normativaChatPage.sendButton')}
          </button>
        </form>
      </div>
    </div>
  );
}
