import type { HttpClient } from '@/application/ports/http-client';
import type { Role } from '@/domain/entities/user';

export class RoleService {
  constructor(private readonly http: HttpClient) {}

  list(): Promise<Role[]> {
    return this.http.get<Role[]>('/roles');
  }

  assignPermission(roleName: string, permissionCode: string): Promise<Role> {
    return this.http.post<Role>(`/roles/${roleName}/permissions`, { permissionCode });
  }
}
