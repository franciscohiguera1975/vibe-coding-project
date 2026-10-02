import { ImagePracticeRunner } from '@/presentation/practices/ImagePracticeRunner';
import { SoftwarePracticeRunner } from '@/presentation/practices/SoftwarePracticeRunner';
import type { PracticeRunnerProps } from '@/presentation/practices/types';
import { UnknownPracticeType } from '@/presentation/practices/UnknownPracticeType';
import type { ComponentType } from 'react';

/** Registro de tipos de practica: agregar una practica de un tipo existente no
 * requiere tocar este archivo (solo una fila en la base de datos); agregar un tipo
 * genuinamente nuevo requiere una entrada aqui (Prompt Maestro §16, §34). */
const REGISTRY: Record<string, ComponentType<PracticeRunnerProps>> = {
  software: SoftwarePracticeRunner,
  image: ImagePracticeRunner,
};

export function getPracticeRunner(type: string): ComponentType<PracticeRunnerProps> {
  return REGISTRY[type] ?? UnknownPracticeType;
}
