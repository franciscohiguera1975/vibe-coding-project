import { aiService } from '@/infrastructure/container';
import { useMutation } from '@tanstack/react-query';

export function useGenerateHint() {
  return useMutation({
    mutationFn: ({ slug, context }: { slug: string; context?: string }) =>
      aiService.generateHint(slug, context),
  });
}

export function useGenerateFeedback() {
  return useMutation({
    mutationFn: (submissionId: string) => aiService.generateFeedback(submissionId),
  });
}
