import type { HttpClient } from '@/application/ports/http-client';
import type { User } from '@/domain/entities/user';

export interface CreateUserInput {
  email: string;
  fullName: string;
  password: string;
  roleNames?: string[];
}

export class UserService {
  constructor(private readonly http: HttpClient) {}

  create(input: CreateUserInput): Promise<User> {
    return this.http.post<User>('/users', input);
  }

  assignRole(userId: string, roleName: string): Promise<User> {
    return this.http.post<User>(`/users/${userId}/roles`, { roleName });
  }
}
