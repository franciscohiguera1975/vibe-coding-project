import type { HttpClient } from '@/application/ports/http-client';
import type {
  PracticeAdminDetail,
  PracticeAttempt,
  PracticeDetail,
  PracticeEvaluation,
  PracticeFilters,
  PracticeNarration,
  PracticeNarrationGenerateAllItem,
  PracticeNarrationGenerated,
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
  /** Overlay de traducciones por idioma (ver PracticeAdminDetail). Solo se
   * envia/edita desde el panel de administracion. */
  translations?: Record<string, unknown>;
}

export class PracticeService {
  constructor(private readonly http: HttpClient) {}

  list(
    filters: PracticeFilters,
    page: number,
    pageSize: number,
    lang?: string,
  ): Promise<Page<PracticeSummary>> {
    return this.http.get<Page<PracticeSummary>>('/practices', {
      ...filters,
      page,
      pageSize,
      lang,
    });
  }

  getBySlug(slug: string, lang?: string): Promise<PracticeDetail> {
    return this.http.get<PracticeDetail>(`/practices/${slug}`, { lang });
  }

  create(input: CreatePracticeInput): Promise<PracticeAdminDetail> {
    return this.http.post<PracticeAdminDetail>('/practices', input);
  }

  update(practiceId: string, input: Partial<CreatePracticeInput>): Promise<PracticeAdminDetail> {
    return this.http.patch<PracticeAdminDetail>(`/practices/${practiceId}`, input);
  }

  publish(practiceId: string): Promise<PracticeAdminDetail> {
    return this.http.post<PracticeAdminDetail>(`/practices/${practiceId}/publish`);
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

  /** Lectura publica del audio narrado ya generado (404 si aun no se genero para
   * ese idioma: el llamador debe tratarlo como estado vacio, no como error). */
  getNarration(slug: string, lang: string): Promise<PracticeNarration> {
    return this.http.get<PracticeNarration>(`/practices/${slug}/narration`, { lang });
  }

  /** Accion deliberada de administracion: dispara la sintesis TTS para un idioma
   * (o la reutiliza si el texto no cambio, ver `cached`). Nunca se llama desde la
   * vista de estudiante. */
  generateNarration(slug: string, lang: string): Promise<PracticeNarrationGenerated> {
    return this.http.post<PracticeNarrationGenerated>(
      `/practices/${slug}/narration?lang=${encodeURIComponent(lang)}`,
    );
  }

  generateAllNarrations(slug: string): Promise<PracticeNarrationGenerateAllItem[]> {
    return this.http.post<PracticeNarrationGenerateAllItem[]>(
      `/practices/${slug}/narration/generate-all`,
    );
  }
}
