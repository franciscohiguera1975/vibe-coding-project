import type { User } from '@/domain/entities/user';
import { useRef, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';

const MENU_CLOSE_DELAY_MS = 200;

function getInitials(fullName: string): string {
  const letters = fullName
    .split(/\s+/)
    .map((word) => word.match(/[\p{L}]/u)?.[0])
    .filter((letter): letter is string => Boolean(letter))
    .slice(0, 2)
    .join('');
  return letters.toUpperCase() || '?';
}

export function UserMenu({ user, onLogout }: { user: User; onLogout: () => void }) {
  const { t } = useTranslation();
  const [open, setOpen] = useState(false);
  const closeTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  function openMenu() {
    if (closeTimer.current) {
      clearTimeout(closeTimer.current);
      closeTimer.current = null;
    }
    setOpen(true);
  }

  function scheduleClose() {
    closeTimer.current = setTimeout(() => setOpen(false), MENU_CLOSE_DELAY_MS);
  }

  return (
    <div className="relative" onMouseEnter={openMenu} onMouseLeave={scheduleClose}>
      <button
        type="button"
        className="flex items-center gap-2 rounded-full p-1 pr-2 transition-colors hover:bg-navy-50"
        onClick={() => setOpen((v) => !v)}
        aria-expanded={open}
        aria-haspopup="menu"
        aria-label={user.fullName}
      >
        <span className="flex h-8 w-8 items-center justify-center rounded-full bg-brand-500 text-xs font-semibold text-white">
          {getInitials(user.fullName)}
        </span>
        <span className="max-w-[8rem] truncate text-sm font-semibold text-navy-700">
          {user.fullName}
        </span>
      </button>

      {open && (
        <div
          role="menu"
          className="absolute right-0 top-full z-50 mt-2 w-60 rounded-md border border-ink-100 bg-white py-2 shadow-lg"
        >
          <div className="border-b border-ink-100 px-4 pb-2">
            <p className="truncate text-sm font-semibold text-navy-900">{user.fullName}</p>
            <p className="truncate text-xs text-ink-500">{user.email}</p>
          </div>
          <Link
            to="/cuenta-y-seguridad"
            role="menuitem"
            className="block px-4 py-2 text-sm font-medium text-navy-700 hover:bg-brand-50 hover:text-brand-600"
            onClick={() => setOpen(false)}
          >
            {t('header.userMenu.accountSecurity')}
          </Link>
          <button
            type="button"
            role="menuitem"
            onClick={() => {
              setOpen(false);
              onLogout();
            }}
            className="block w-full px-4 py-2 text-left text-sm font-medium text-navy-700 hover:bg-brand-50 hover:text-brand-600"
          >
            {t('header.logout')}
          </button>
        </div>
      )}
    </div>
  );
}
