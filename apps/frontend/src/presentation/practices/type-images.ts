import categoryImages1 from '@/assets/home/category-images-practice-2.jpg';
import categoryImages2 from '@/assets/home/category-images-practice.jpg';
import categoryImages3 from '@/assets/home/category-images-practice-3.jpg';
import categorySoftware from '@/assets/home/category-software.jpg';
import categorySoftware2 from '@/assets/home/category-software-2.jpg';
import heroSoftware1 from '@/assets/home/hero-software-1.jpg';
import heroSoftware2 from '@/assets/home/hero-software-2.jpg';

/** Portadas genéricas por tipo de práctica (no son capturas reales de cada una
 * — no existen capturas por práctica en el modelo de datos). Varias por tipo
 * para que prácticas del mismo tipo, mostradas una junto a otra, no repitan
 * exactamente la misma imagen. La elección es determinística por id (no
 * aleatoria en cada render): la misma práctica siempre muestra la misma
 * portada, pero dos prácticas distintas del mismo tipo casi nunca coinciden. */
const PRACTICE_TYPE_COVERS: Record<string, string[]> = {
  software: [heroSoftware1, heroSoftware2, categorySoftware, categorySoftware2],
  image: [categoryImages1, categoryImages2, categoryImages3],
};

function hashString(value: string): number {
  let hash = 0;
  for (let i = 0; i < value.length; i++) {
    hash = (hash * 31 + value.charCodeAt(i)) | 0;
  }
  return Math.abs(hash);
}

export function getPracticeTypeCover(type: string, seed = type): string {
  const pool = PRACTICE_TYPE_COVERS[type] ?? PRACTICE_TYPE_COVERS.software;
  return pool[hashString(seed) % pool.length];
}
