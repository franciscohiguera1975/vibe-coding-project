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
