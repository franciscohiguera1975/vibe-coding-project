import type { PracticeDetail } from '@/domain/entities/practice';

export interface PracticeRunnerProps {
  practice: PracticeDetail;
  onSubmit: (payload: Record<string, unknown>) => Promise<void>;
  isSubmitting: boolean;
}
