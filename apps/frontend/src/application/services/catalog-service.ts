import type { HttpClient } from '@/application/ports/http-client';
import type { PracticeCategory, PracticeTag } from '@/domain/entities/catalog';

export class CatalogService {
  constructor(private readonly http: HttpClient) {}

  listCategories(): Promise<PracticeCategory[]> {
    return this.http.get<PracticeCategory[]>('/practice-categories');
  }

  createCategory(name: string, slug?: string): Promise<PracticeCategory> {
    return this.http.post<PracticeCategory>('/practice-categories', { name, slug });
  }

  listTags(): Promise<PracticeTag[]> {
    return this.http.get<PracticeTag[]>('/practice-tags');
  }

  createTag(name: string): Promise<PracticeTag> {
    return this.http.post<PracticeTag>('/practice-tags', { name });
  }
}
