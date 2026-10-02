import {
  catalogService,
  roleService,
  systemService,
  userService,
} from '@/infrastructure/container';
import type { CreateUserInput } from '@/application/services/user-service';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

export function useUsers(page: number) {
  return useQuery({
    queryKey: ['admin', 'users', page],
    queryFn: () => userService.list(page),
  });
}

export function useCreateUser() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (input: CreateUserInput) => userService.create(input),
    onSuccess: () => void queryClient.invalidateQueries({ queryKey: ['admin', 'users'] }),
  });
}

export function useAssignRole() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ userId, roleName }: { userId: string; roleName: string }) =>
      userService.assignRole(userId, roleName),
    onSuccess: () => void queryClient.invalidateQueries({ queryKey: ['admin', 'users'] }),
  });
}

export function useRoles() {
  return useQuery({ queryKey: ['admin', 'roles'], queryFn: () => roleService.list() });
}

export function usePermissions() {
  return useQuery({
    queryKey: ['admin', 'permissions'],
    queryFn: () => roleService.listPermissions(),
  });
}

export function useAssignPermission() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ roleName, permissionCode }: { roleName: string; permissionCode: string }) =>
      roleService.assignPermission(roleName, permissionCode),
    onSuccess: () => void queryClient.invalidateQueries({ queryKey: ['admin', 'roles'] }),
  });
}

export function useCategories() {
  return useQuery({
    queryKey: ['admin', 'categories'],
    queryFn: () => catalogService.listCategories(),
  });
}

export function useCreateCategory() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (name: string) => catalogService.createCategory(name),
    onSuccess: () => void queryClient.invalidateQueries({ queryKey: ['admin', 'categories'] }),
  });
}

export function useConfigurations() {
  return useQuery({
    queryKey: ['admin', 'configurations'],
    queryFn: () => systemService.listConfigurations(),
  });
}

export function useUpdateConfiguration() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      key,
      value,
      description,
    }: {
      key: string;
      value: Record<string, unknown>;
      description?: string;
    }) => systemService.updateConfiguration(key, value, description),
    onSuccess: () => void queryClient.invalidateQueries({ queryKey: ['admin', 'configurations'] }),
  });
}

export function useAuditLogs(page: number) {
  return useQuery({
    queryKey: ['admin', 'audit-logs', page],
    queryFn: () => systemService.listAuditLogs(page),
  });
}
