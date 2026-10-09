import { ApiError } from '@/application/ports/http-client';
import { practiceService } from '@/infrastructure/container';
import type { PracticeFilters, PracticeNarration } from '@/domain/entities/practice';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useTranslation } from 'react-i18next';

export function usePractices(filters: PracticeFilters, page: number, pageSize = 12) {
  const {
    i18n: { language },
  } = useTranslation();
  return useQuery({
    queryKey: ['practices', filters, page, pageSize, language],
    queryFn: () => practiceService.list(filters, page, pageSize, language),
  });
}

export function usePractice(slug: string | undefined) {
  const {
    i18n: { language },
  } = useTranslation();
  return useQuery({
    queryKey: ['practice', slug, language],
    queryFn: () => practiceService.getBySlug(slug as string, language),
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

/** Audio narrado ya generado para el idioma activo. Un 404 (narracion no generada
 * todavia para ese idioma) es un estado vacio normal, nunca un error de carga:
 * `data` queda `null` y el llamador muestra el estado "no disponible aun". */
export function usePracticeNarration(slug: string | undefined) {
  const {
    i18n: { language },
  } = useTranslation();
  return useQuery({
    queryKey: ['practice-narration', slug, language],
    queryFn: async (): Promise<PracticeNarration | null> => {
      try {
        return await practiceService.getNarration(slug as string, language);
      } catch (error) {
        if (error instanceof ApiError && error.status === 404) return null;
        throw error;
      }
    },
    enabled: Boolean(slug),
  });
}

export function useGenerateAllNarrations() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (slug: string) => practiceService.generateAllNarrations(slug),
    onSuccess: (_result, slug) => {
      void queryClient.invalidateQueries({ queryKey: ['practice-narration', slug] });
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
