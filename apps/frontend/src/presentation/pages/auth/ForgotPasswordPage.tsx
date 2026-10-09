import { authService } from '@/infrastructure/container';
import { ApiError } from '@/application/ports/http-client';
import { FormEvent, useState } from 'react';
import { Trans, useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';

export function ForgotPasswordPage() {
  const { t } = useTranslation();
  const [email, setEmail] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isSent, setIsSent] = useState(false);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setError(null);
    setIsSubmitting(true);
    try {
      await authService.requestPasswordReset(email);
      setIsSent(true);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : t('forgotPasswordPage.errors.generic'));
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <div className="mx-auto flex min-h-[70vh] max-w-md flex-col justify-center px-4 py-16">
      <h1 className="text-2xl font-semibold text-ink-900">{t('forgotPasswordPage.title')}</h1>
      <p className="mt-1 text-sm text-ink-500">{t('forgotPasswordPage.subtitle')}</p>

      {isSent ? (
        <div className="card mt-6 space-y-4 p-6">
          <p className="text-sm text-emerald-700">
            <Trans
              i18nKey="forgotPasswordPage.sentMessage"
              values={{ email }}
              components={{ strong: <strong /> }}
            />
          </p>
          <Link to="/login" className="text-sm font-medium text-brand-600 hover:underline">
            {t('forgotPasswordPage.backToLogin')}
          </Link>
        </div>
      ) : (
        <form onSubmit={handleSubmit} className="card mt-6 space-y-4 p-6">
          <div>
            <label htmlFor="email" className="label">
              {t('forgotPasswordPage.emailLabel')}
            </label>
            <input
              id="email"
              type="email"
              required
              className="input"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              autoComplete="email"
            />
          </div>

          {error && <p className="text-sm text-rose-600">{error}</p>}

          <button type="submit" className="btn-primary w-full" disabled={isSubmitting}>
            {isSubmitting ? t('forgotPasswordPage.submitting') : t('forgotPasswordPage.submit')}
          </button>

          <Link
            to="/login"
            className="block text-center text-sm font-medium text-brand-600 hover:underline"
          >
            {t('forgotPasswordPage.backToLogin')}
          </Link>
        </form>
      )}
    </div>
  );
}
