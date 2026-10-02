import type { TokenStorage } from '@/application/ports/token-storage';

const ACCESS_KEY = 'vibe_coding.access_token';
const REFRESH_KEY = 'vibe_coding.refresh_token';

export class LocalTokenStorage implements TokenStorage {
  getAccessToken(): string | null {
    return localStorage.getItem(ACCESS_KEY);
  }

  getRefreshToken(): string | null {
    return localStorage.getItem(REFRESH_KEY);
  }

  setTokens(accessToken: string, refreshToken: string): void {
    localStorage.setItem(ACCESS_KEY, accessToken);
    localStorage.setItem(REFRESH_KEY, refreshToken);
  }

  clear(): void {
    localStorage.removeItem(ACCESS_KEY);
    localStorage.removeItem(REFRESH_KEY);
  }
}

export const tokenStorage = new LocalTokenStorage();
