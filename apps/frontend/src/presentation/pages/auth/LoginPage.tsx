import { useAuth } from '@/application/hooks/auth-context';
import { ApiError } from '@/application/ports/http-client';
import { FormEvent, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Link, useLocation, useNavigate } from 'react-router-dom';

export function LoginPage() {
  const { t } = useTranslation();
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setError(null);
    setIsSubmitting(true);
    try {
      await login(email, password);
      const redirectTo = (location.state as { from?: string } | null)?.from ?? '/';
      navigate(redirectTo, { replace: true });
    } catch (err) {
      setError(err instanceof ApiError ? err.message : t('loginPage.errors.generic'));
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <div className="mx-auto flex min-h-[70vh] max-w-md flex-col justify-center px-4 py-16">
      <h1 className="text-2xl font-semibold text-ink-900">{t('loginPage.title')}</h1>
      <p className="mt-1 text-sm text-ink-500">{t('loginPage.subtitle')}</p>

      <form onSubmit={handleSubmit} className="card mt-6 space-y-4 p-6">
        <div>
          <label htmlFor="email" className="label">
            {t('loginPage.emailLabel')}
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
        <div>
          <label htmlFor="password" className="label">
            {t('loginPage.passwordLabel')}
          </label>
          <input
            id="password"
            type="password"
            required
            className="input"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            autoComplete="current-password"
          />
          <Link
            to="/recuperar-contrasena"
            className="mt-1 inline-block text-sm font-medium text-brand-600 hover:underline"
          >
            {t('loginPage.forgotPassword')}
          </Link>
        </div>

        {error && <p className="text-sm text-rose-600">{error}</p>}

        <button type="submit" className="btn-primary w-full" disabled={isSubmitting}>
          {isSubmitting ? t('loginPage.submitting') : t('loginPage.submit')}
        </button>
      </form>
    </div>
  );
}
