import { imageService } from '@/infrastructure/container';
import { useMutation } from '@tanstack/react-query';

export function useAnalyzeImage() {
  return useMutation({
    mutationFn: ({ slug, file }: { slug: string; file: File }) => imageService.analyze(slug, file),
  });
}
