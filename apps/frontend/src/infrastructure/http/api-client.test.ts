import type { TokenStorage } from '@/application/ports/token-storage';
import { ApiClient } from '@/infrastructure/http/api-client';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

function fakeTokenStorage(): TokenStorage {
  return {
    getAccessToken: () => 'access-token',
    getRefreshToken: () => 'refresh-token',
    setTokens: vi.fn(),
    clear: vi.fn(),
  };
}

function jsonResponse(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { 'Content-Type': 'application/json' },
  });
}

describe('ApiClient key-case transform', () => {
  let fetchMock: ReturnType<typeof vi.fn>;

  beforeEach(() => {
    fetchMock = vi.fn();
    vi.stubGlobal('fetch', fetchMock);
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it('converts top-level response keys to camelCase', async () => {
    fetchMock.mockResolvedValue(jsonResponse({ estimated_time_minutes: 45 }));
    const client = new ApiClient(fakeTokenStorage());

    const result = await client.get<{ estimatedTimeMinutes: number }>('/practices/x');

    expect(result).toEqual({ estimatedTimeMinutes: 45 });
  });

  it('does NOT transform keys inside opaque JSONB fields like `content`', async () => {
    // Regresion del bug real encontrado en verificacion manual: el transform
    // recursivo convertia content.speed_kmh en content.speedKmh, lo que rompia
    // silenciosamente la deteccion `'speed_kmh' in variables` del runner.
    fetchMock.mockResolvedValue(
      jsonResponse({
        content: { model: { variables: { speed_kmh: { min: 0, max: 100 } } } },
      }),
    );
    const client = new ApiClient(fakeTokenStorage());

    const result = await client.get<{ content: Record<string, unknown> }>('/practices/x');

    expect(result.content).toEqual({
      model: { variables: { speed_kmh: { min: 0, max: 100 } } },
    });
  });

  it('converts camelCase request body keys to snake_case before sending, except opaque fields', async () => {
    fetchMock.mockResolvedValue(jsonResponse({}));
    const client = new ApiClient(fakeTokenStorage());

    await client.post('/practices', {
      estimatedTimeMinutes: 45,
      content: { speedKmh: 60 },
    });

    const [, init] = fetchMock.mock.calls[0];
    const sentBody = JSON.parse(init.body as string);
    expect(sentBody).toEqual({
      estimated_time_minutes: 45,
      content: { speedKmh: 60 },
    });
  });
});
