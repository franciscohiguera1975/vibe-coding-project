import type { HttpClient } from '@/application/ports/http-client';
import type { ChecklistItemResult, RagEvaluationRun } from '@/domain/entities/rag';

export class RagService {
  constructor(private readonly http: HttpClient) {}

  validateSyllabus(text: string): Promise<ChecklistItemResult[]> {
    return this.http.post<ChecklistItemResult[]>('/rag/validate-syllabus', { text });
  }

  validateSyllabusFile(file: File): Promise<ChecklistItemResult[]> {
    const formData = new FormData();
    formData.append('file', file);
    return this.http.uploadFile<ChecklistItemResult[]>('/rag/validate-syllabus/upload', formData);
  }

  getLatestEvaluation(): Promise<RagEvaluationRun> {
    return this.http.get<RagEvaluationRun>('/rag/evaluation');
  }

  runEvaluation(): Promise<RagEvaluationRun> {
    return this.http.post<RagEvaluationRun>('/rag/evaluation/run');
  }
}
