import type { HttpClient } from '@/application/ports/http-client';
import type { AuthTokens, User } from '@/domain/entities/user';

export class AuthService {
  constructor(private readonly http: HttpClient) {}

  login(email: string, password: string): Promise<AuthTokens> {
    return this.http.post<AuthTokens>('/auth/login', { email, password });
  }

  me(): Promise<User> {
    return this.http.get<User>('/auth/me');
  }
}
