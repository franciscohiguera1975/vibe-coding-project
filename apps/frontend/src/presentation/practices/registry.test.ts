import { ImagePracticeRunner } from '@/presentation/practices/ImagePracticeRunner';
import { getPracticeRunner } from '@/presentation/practices/registry';
import { SoftwarePracticeRunner } from '@/presentation/practices/SoftwarePracticeRunner';
import { UnknownPracticeType } from '@/presentation/practices/UnknownPracticeType';
import { describe, expect, it } from 'vitest';

describe('getPracticeRunner', () => {
  it('resolves the software runner for type "software"', () => {
    expect(getPracticeRunner('software')).toBe(SoftwarePracticeRunner);
  });

  it('resolves the image runner for type "image"', () => {
    expect(getPracticeRunner('image')).toBe(ImagePracticeRunner);
  });

  it('falls back to UnknownPracticeType for an unregistered type', () => {
    expect(getPracticeRunner('quiz')).toBe(UnknownPracticeType);
  });
});
