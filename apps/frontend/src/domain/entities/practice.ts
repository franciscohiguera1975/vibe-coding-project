export type PracticeDifficulty = 'beginner' | 'intermediate' | 'advanced';
export type PracticeStatus = 'draft' | 'published' | 'archived';

export interface PracticeSummary {
  id: string;
  slug: string;
  title: string;
  description: string;
  type: string;
  difficulty: PracticeDifficulty;
  estimatedTimeMinutes: number;
  technologies: string[];
  status: PracticeStatus;
  categoryId: string | null;
}

export interface PracticeDetail extends PracticeSummary {
  objectives: string[];
  instructions: string;
  content: Record<string, unknown>;
  evaluation: Record<string, unknown>;
  aiConfiguration: Record<string, unknown>;
  embeddingConfiguration: Record<string, unknown>;
  metadata: Record<string, unknown>;
}

export interface PracticeAttempt {
  id: string;
  practiceId: string;
  attemptNumber: number;
  status: 'in_progress' | 'submitted' | 'evaluated' | 'abandoned';
  startedAt: string;
  finishedAt: string | null;
}

export interface PracticeSubmission {
  id: string;
  attemptId: string;
  submittedAt: string;
}

export interface PracticeEvaluation {
  id: string;
  submissionId: string;
  score: number;
  passed: boolean;
  feedback: string;
  details: Record<string, unknown>;
}

export interface PracticeFilters {
  categoryId?: string;
  difficulty?: PracticeDifficulty;
  technology?: string;
  type?: string;
  status?: PracticeStatus;
  hasAi?: boolean;
  search?: string;
}

export interface PracticeNarration {
  lang: string;
  url: string;
}

export interface PracticeNarrationGenerated extends PracticeNarration {
  cached: boolean;
}

export interface PracticeNarrationGenerateAllItem {
  lang: string;
  status: 'ok' | 'error';
  url?: string | null;
  cached?: boolean | null;
  message?: string | null;
}

export interface PracticeAdminDetail extends PracticeDetail {
  /** Traducciones crudas por idioma (solo expuestas por los endpoints de
   * administracion: crear/actualizar/publicar). No se usa para renderizar la
   * practica — eso ya viene localizado en los campos de PracticeDetail segun el
   * `lang` enviado en la solicitud. */
  translations: Record<string, unknown>;
}
