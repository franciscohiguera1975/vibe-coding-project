import type { HttpClient } from '@/application/ports/http-client';
import type {
  PracticeAttempt,
  PracticeDetail,
  PracticeEvaluation,
  PracticeFilters,
  PracticeSubmission,
  PracticeSummary,
} from '@/domain/entities/practice';
import type { Page } from '@/shared/types/page';

export interface CreatePracticeInput {
  title: string;
  type: string;
  slug?: string;
  description?: string;
  objectives?: string[];
  instructions?: string;
  categorySlug?: string;
  difficulty?: string;
  estimatedTimeMinutes?: number;
  technologies?: string[];
  tagNames?: string[];
  content?: Record<string, unknown>;
  evaluation?: Record<string, unknown>;
  aiConfiguration?: Record<string, unknown>;
  embeddingConfiguration?: Record<string, unknown>;
  metadata?: Record<string, unknown>;
}

export class PracticeService {
  constructor(private readonly http: HttpClient) {}

  list(filters: PracticeFilters, page: number, pageSize: number): Promise<Page<PracticeSummary>> {
    return this.http.get<Page<PracticeSummary>>('/practices', {
      ...filters,
      page,
      pageSize,
    });
  }

  getBySlug(slug: string): Promise<PracticeDetail> {
    return this.http.get<PracticeDetail>(`/practices/${slug}`);
  }

  create(input: CreatePracticeInput): Promise<PracticeDetail> {
    return this.http.post<PracticeDetail>('/practices', input);
  }

  update(practiceId: string, input: Partial<CreatePracticeInput>): Promise<PracticeDetail> {
    return this.http.patch<PracticeDetail>(`/practices/${practiceId}`, input);
  }

  publish(practiceId: string): Promise<PracticeDetail> {
    return this.http.post<PracticeDetail>(`/practices/${practiceId}/publish`);
  }

  start(slug: string): Promise<PracticeAttempt> {
    return this.http.post<PracticeAttempt>(`/practices/${slug}/start`);
  }

  submit(attemptId: string, payload: Record<string, unknown>): Promise<PracticeSubmission> {
    return this.http.post<PracticeSubmission>('/practices/attempts/submit', {
      attemptId,
      payload,
    });
  }

  evaluate(submissionId: string): Promise<PracticeEvaluation> {
    return this.http.post<PracticeEvaluation>(`/practices/submissions/${submissionId}/evaluate`);
  }
}
