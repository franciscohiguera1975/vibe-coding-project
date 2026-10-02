import type { HttpClient } from '@/application/ports/http-client';

export interface AgentRunResult {
  sessionId: string;
  response: string;
  iterationsUsed: number;
  tokensUsed: number;
}

export class AgentService {
  constructor(private readonly http: HttpClient) {}

  run(practiceSlug: string, userMessage: string): Promise<AgentRunResult> {
    return this.http.post<AgentRunResult>('/agent/run', { practiceSlug, userMessage });
  }
}
