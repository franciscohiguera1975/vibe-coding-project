import type { HttpClient } from '@/application/ports/http-client';
import type { AuditLog, Configuration } from '@/domain/entities/system';
import type { Page } from '@/shared/types/page';

export class SystemService {
  constructor(private readonly http: HttpClient) {}

  listConfigurations(): Promise<Configuration[]> {
    return this.http.get<Configuration[]>('/configurations');
  }

  updateConfiguration(
    key: string,
    value: Record<string, unknown>,
    description = '',
  ): Promise<Configuration> {
    return this.http.put<Configuration>(`/configurations/${key}`, { value, description });
  }

  listAuditLogs(page: number, pageSize = 20): Promise<Page<AuditLog>> {
    return this.http.get<Page<AuditLog>>('/audit-logs', { page, pageSize });
  }
}
