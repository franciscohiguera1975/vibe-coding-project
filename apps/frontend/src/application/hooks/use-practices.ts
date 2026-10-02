import { practiceService } from '@/infrastructure/container';
import type { PracticeFilters } from '@/domain/entities/practice';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

export function usePractices(filters: PracticeFilters, page: number, pageSize = 12) {
  return useQuery({
    queryKey: ['practices', filters, page, pageSize],
    queryFn: () => practiceService.list(filters, page, pageSize),
  });
}

export function usePractice(slug: string | undefined) {
  return useQuery({
    queryKey: ['practice', slug],
    queryFn: () => practiceService.getBySlug(slug as string),
    enabled: Boolean(slug),
  });
}

export function useStartPractice() {
  return useMutation({
    mutationFn: (slug: string) => practiceService.start(slug),
  });
}

export function useSubmitPractice() {
  return useMutation({
    mutationFn: ({ attemptId, payload }: { attemptId: string; payload: Record<string, unknown> }) =>
      practiceService.submit(attemptId, payload),
  });
}

export function useEvaluatePractice() {
  return useMutation({
    mutationFn: (submissionId: string) => practiceService.evaluate(submissionId),
  });
}

export function usePublishPractice() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (practiceId: string) => practiceService.publish(practiceId),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['practices'] });
    },
  });
}

export function useCreatePractice() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: practiceService.create.bind(practiceService),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['practices'] });
    },
  });
}
