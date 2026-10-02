export interface User {
  id: string;
  email: string;
  fullName: string;
  isActive: boolean;
  roles: string[];
  permissions: string[];
}

export interface AuthTokens {
  accessToken: string;
  refreshToken: string;
  tokenType: string;
  user: User;
}

export interface Role {
  id: string;
  name: string;
  description: string;
  permissions: { code: string; description: string }[];
}
