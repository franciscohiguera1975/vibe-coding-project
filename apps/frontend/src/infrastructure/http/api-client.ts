import { ApiError, type HttpClient } from '@/application/ports/http-client';
import type { TokenStorage } from '@/application/ports/token-storage';
import type { AuthTokens } from '@/domain/entities/user';
import { tokenStorage } from '@/infrastructure/auth/local-token-storage';

const BASE_URL = `${import.meta.env.VITE_API_URL ?? 'http://localhost:3000'}/api`;

function toSnakeKey(key: string): string {
  return key.replace(/[A-Z]/g, (c) => `_${c.toLowerCase()}`);
}

function buildQuery(params?: Record<string, unknown>): string {
  if (!params) return '';
  const entries = Object.entries(params).filter(
    ([, v]) => v !== undefined && v !== null && v !== '',
  );
  if (entries.length === 0) return '';
  const search = new URLSearchParams();
  for (const [key, value] of entries) search.set(toSnakeKey(key), String(value));
  return `?${search.toString()}`;
}

/** Campos JSONB de contenido libre definido por quien autora la practica (no son
 * nombres de esquema de la API): sus claves internas (p.ej. `speed_kmh`) deben
 * preservarse tal cual, nunca convertirse a camelCase/snake_case. */
const OPAQUE_KEYS = new Set([
  'content',
  'evaluation',
  'aiConfiguration',
  'ai_configuration',
  'embeddingConfiguration',
  'embedding_configuration',
  'metadata',
  'details',
  'value',
  'payload',
]);

function toCamelCase(value: unknown): unknown {
  if (Array.isArray(value)) return value.map(toCamelCase);
  if (value !== null && typeof value === 'object') {
    return Object.fromEntries(
      Object.entries(value as Record<string, unknown>).map(([key, v]) => {
        const camelKey = key.replace(/_([a-z])/g, (_, c: string) => c.toUpperCase());
        return [camelKey, OPAQUE_KEYS.has(camelKey) ? v : toCamelCase(v)];
      }),
    );
  }
  return value;
}

function toSnakeCase(value: unknown): unknown {
  if (Array.isArray(value)) return value.map(toSnakeCase);
  if (value !== null && typeof value === 'object') {
    return Object.fromEntries(
      Object.entries(value as Record<string, unknown>).map(([key, v]) => {
        const snakeKey = key.replace(/[A-Z]/g, (c) => `_${c.toLowerCase()}`);
        return [snakeKey, OPAQUE_KEYS.has(key) ? v : toSnakeCase(v)];
      }),
    );
  }
  return value;
}

/** Implementa el puerto HttpClient. Aisla fetch, auth y el (des)mapeo snake_case
 * <-> camelCase para que el resto del frontend nunca vea el formato HTTP crudo. */
export class ApiClient implements HttpClient {
  private refreshPromise: Promise<void> | null = null;

  constructor(private readonly tokens: TokenStorage) {}

  get<T>(path: string, params?: Record<string, unknown>): Promise<T> {
    return this.request<T>('GET', `${path}${buildQuery(params)}`);
  }

  post<T>(path: string, body?: unknown): Promise<T> {
    return this.request<T>('POST', path, body);
  }

  put<T>(path: string, body?: unknown): Promise<T> {
    return this.request<T>('PUT', path, body);
  }

  patch<T>(path: string, body?: unknown): Promise<T> {
    return this.request<T>('PATCH', path, body);
  }

  delete<T>(path: string): Promise<T> {
    return this.request<T>('DELETE', path);
  }

  async uploadFile<T>(path: string, formData: FormData, isRetry = false): Promise<T> {
    const headers: Record<string, string> = {};
    const accessToken = this.tokens.getAccessToken();
    if (accessToken) headers.Authorization = `Bearer ${accessToken}`;

    // Sin Content-Type: el navegador fija el boundary multipart automaticamente.
    const response = await fetch(`${BASE_URL}${path}`, { method: 'POST', headers, body: formData });

    if (response.status === 401 && !isRetry) {
      const refreshed = await this.refreshAccessToken();
      if (refreshed) return this.uploadFile<T>(path, formData, true);
      this.tokens.clear();
    }

    const text = await response.text();
    const data = text ? JSON.parse(text) : undefined;

    if (!response.ok) {
      throw new ApiError(response.status, extractErrorMessage(data) ?? response.statusText);
    }
    return toCamelCase(data) as T;
  }

  private async request<T>(
    method: string,
    path: string,
    body?: unknown,
    isRetry = false,
  ): Promise<T> {
    const headers: Record<string, string> = { 'Content-Type': 'application/json' };
    const accessToken = this.tokens.getAccessToken();
    if (accessToken) headers.Authorization = `Bearer ${accessToken}`;

    const response = await fetch(`${BASE_URL}${path}`, {
      method,
      headers,
      body: body !== undefined ? JSON.stringify(toSnakeCase(body)) : undefined,
    });

    if (response.status === 401 && !isRetry && !path.startsWith('/auth/')) {
      const refreshed = await this.refreshAccessToken();
      if (refreshed) return this.request<T>(method, path, body, true);
      this.tokens.clear();
    }

    if (response.status === 204) return undefined as T;

    const text = await response.text();
    const data = text ? JSON.parse(text) : undefined;

    if (!response.ok) {
      const message = extractErrorMessage(data) ?? response.statusText;
      throw new ApiError(response.status, message);
    }

    return toCamelCase(data) as T;
  }

  private async refreshAccessToken(): Promise<boolean> {
    const refreshToken = this.tokens.getRefreshToken();
    if (!refreshToken) return false;

    this.refreshPromise ??= (async () => {
      const response = await fetch(`${BASE_URL}/auth/refresh`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh_token: refreshToken }),
      });
      if (!response.ok) throw new Error('refresh failed');
      const data = (toCamelCase(await response.json()) as AuthTokens) ?? null;
      if (data) this.tokens.setTokens(data.accessToken, data.refreshToken);
    })().finally(() => {
      this.refreshPromise = null;
    });

    try {
      await this.refreshPromise;
      return true;
    } catch {
      return false;
    }
  }
}

function extractErrorMessage(data: unknown): string | null {
  if (!data || typeof data !== 'object') return null;
  const detail = (data as { detail?: unknown }).detail;
  if (typeof detail === 'string') return detail;
  if (Array.isArray(detail)) {
    return detail
      .map((item) => (typeof item === 'object' && item && 'msg' in item ? String(item.msg) : null))
      .filter(Boolean)
      .join(', ');
  }
  return null;
}

export const apiClient = new ApiClient(tokenStorage);
