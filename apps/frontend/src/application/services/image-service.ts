import type { HttpClient } from '@/application/ports/http-client';

export interface ImageAnalysisResult {
  key: string;
  url: string;
  count: number;
  warnings: string[];
  details: Record<string, unknown>;
}

export class ImageService {
  constructor(private readonly http: HttpClient) {}

  analyze(practiceSlug: string, file: File): Promise<ImageAnalysisResult> {
    const formData = new FormData();
    formData.append('practice_slug', practiceSlug);
    formData.append('file', file);
    return this.http.uploadFile<ImageAnalysisResult>('/images/analyze', formData);
  }
}
