import type { HttpClient } from '@/application/ports/http-client';

export class AiService {
  constructor(private readonly http: HttpClient) {}

  generateHint(practiceSlug: string, studentContext = ''): Promise<{ hint: string }> {
    return this.http.post<{ hint: string }>('/ai/hint', { practiceSlug, studentContext });
  }

  generateFeedback(submissionId: string): Promise<{ feedback: string }> {
    return this.http.post<{ feedback: string }>('/ai/feedback', { submissionId });
  }
}
