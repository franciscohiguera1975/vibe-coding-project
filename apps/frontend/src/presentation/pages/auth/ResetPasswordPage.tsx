import { authService } from '@/infrastructure/container';
import { ApiError } from '@/application/ports/http-client';
import { FormEvent, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';

export function ResetPasswordPage() {
  const { t } = useTranslation();
  const [searchParams] = useSearchParams();
  const token = searchParams.get('token') ?? '';
  const navigate = useNavigate();

  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isDone, setIsDone] = useState(false);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setError(null);

    if (newPassword !== confirmPassword) {
      setError(t('resetPasswordPage.errors.mismatch'));
      return;
    }

    setIsSubmitting(true);
    try {
      await authService.resetPassword(token, newPassword);
      setIsDone(true);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : t('resetPasswordPage.errors.generic'));
    } finally {
      setIsSubmitting(false);
    }
  }

  if (!token) {
    return (
      <div className="mx-auto flex min-h-[70vh] max-w-md flex-col justify-center px-4 py-16">
        <h1 className="text-2xl font-semibold text-ink-900">
          {t('resetPasswordPage.invalidLink.title')}
        </h1>
        <p className="card mt-6 p-6 text-sm text-rose-600">
          {t('resetPasswordPage.invalidLink.description')}
        </p>
        <Link
          to="/recuperar-contrasena"
          className="mt-4 text-center text-sm font-medium text-brand-600 hover:underline"
        >
          {t('resetPasswordPage.invalidLink.requestNew')}
        </Link>
      </div>
    );
  }

  return (
    <div className="mx-auto flex min-h-[70vh] max-w-md flex-col justify-center px-4 py-16">
      <h1 className="text-2xl font-semibold text-ink-900">{t('resetPasswordPage.title')}</h1>
      <p className="mt-1 text-sm text-ink-500">{t('resetPasswordPage.subtitle')}</p>

      {isDone ? (
        <div className="card mt-6 space-y-4 p-6">
          <p className="text-sm text-emerald-700">{t('resetPasswordPage.success.message')}</p>
          <button className="btn-primary w-full" onClick={() => navigate('/login')}>
            {t('resetPasswordPage.success.goToLogin')}
          </button>
        </div>
      ) : (
        <form onSubmit={handleSubmit} className="card mt-6 space-y-4 p-6">
          <div>
            <label htmlFor="newPassword" className="label">
              {t('resetPasswordPage.newPasswordLabel')}
            </label>
            <input
              id="newPassword"
              type="password"
              required
              minLength={8}
              className="input"
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              autoComplete="new-password"
            />
          </div>
          <div>
            <label htmlFor="confirmPassword" className="label">
              {t('resetPasswordPage.confirmPasswordLabel')}
            </label>
            <input
              id="confirmPassword"
              type="password"
              required
              minLength={8}
              className="input"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              autoComplete="new-password"
            />
          </div>

          {error && <p className="text-sm text-rose-600">{error}</p>}

          <button type="submit" className="btn-primary w-full" disabled={isSubmitting}>
            {isSubmitting ? t('resetPasswordPage.submitting') : t('resetPasswordPage.submit')}
          </button>
        </form>
      )}
    </div>
  );
}
