import { ApiError } from '@/application/ports/http-client';
import { ragService } from '@/infrastructure/container';
import type { RagEvaluationRun } from '@/domain/entities/rag';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

export function useValidateSyllabus() {
  return useMutation({
    mutationFn: (text: string) => ragService.validateSyllabus(text),
  });
}

export function useValidateSyllabusFile() {
  return useMutation({
    mutationFn: (file: File) => ragService.validateSyllabusFile(file),
  });
}

/** Un 404 (aun no se corrio ninguna evaluacion) es un estado vacio normal, no un
 * error de carga — mismo patron que usePracticeNarration. */
export function useLatestRagEvaluation() {
  return useQuery({
    queryKey: ['rag-evaluation-latest'],
    queryFn: async (): Promise<RagEvaluationRun | null> => {
      try {
        return await ragService.getLatestEvaluation();
      } catch (error) {
        if (error instanceof ApiError && error.status === 404) return null;
        throw error;
      }
    },
  });
}

export function useRunRagEvaluation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () => ragService.runEvaluation(),
    onSuccess: (run) => {
      queryClient.setQueryData(['rag-evaluation-latest'], run);
    },
  });
}
