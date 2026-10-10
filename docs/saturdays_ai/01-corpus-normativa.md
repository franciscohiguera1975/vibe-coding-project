# Corpus de normativa — inventario

Documentos reales recopilados por el usuario en `docs/reglamentos_ute/` (no se commitean al repo de la plataforma — son propiedad institucional de la UTE, se tratan como dato local para el RAG, igual que `docs/CINCO MINUTOS PROYECTO/` se mantuvo fuera del repo).

| Documento | Páginas | Rol para la validación de sílabos |
|---|---|---|
| LOES 2025.pdf | 71 | Marco legal general (Ley Orgánica de Educación Superior) — base jurídica de más alto nivel. |
| Reglamento de Régimen Académico CODIFICADO 09_03_23.pdf | 42 | **Núcleo del caso de uso**: aquí se define qué debe contener un sílabo, créditos, horas, modalidades. |
| Reglamento de Carrera y Escalafón del Personal Académico CODIFICADO 27_02_24.pdf | 106 | Relevante para el próximo paso (distributivo de carga horaria docente), no para sílabos. |
| Reglamento del Estudiante (Codificación)-Septiembre 2026.pdf | 33 | Contexto estudiantil (evaluación, derechos) — aplica parcialmente a sílabos (criterios de evaluación). |
| RESOLUCION_No._069-SE-11-CU-UTE-2026_REFORMA_REGLAMENTO_ESTUDIANTE (1).pdf | 4 | Reforma puntual al reglamento del estudiante — se indexa junto al anterior. |
| REGLAMENTO DE POSGRADOS DE LA UTE...2017.pdf | 19 | Aplica solo si el sílabo es de posgrado. |
| RESOLUCIÓN RECTORAL No. 008-R-UTE-2023-INSTRUCTIVO POSGRADOS CCSS.pdf | 10 | Instructivo específico de posgrados (Ciencias Sociales y de la Salud). |
| 120_Instructivo_Perfeccionamiento_Academico1_signed (1).pdf | 11 | Perfeccionamiento docente — tangencial. |
| Instructivo Segunda Lengua.pdf | 12 | Requisito de segunda lengua — puede aplicar a ciertos sílabos. |
| Sistema de Evaluación POSGRADOS EN LINEA.pdf | 3 | Evaluación específica de posgrados en línea. |

**Total: ~311 páginas, 10 documentos → 896 chunks extraídos** (ejecutado 2026-10-09 con `apps/backend/scripts/rag/ingest_normativa.py`, chunking por artículo).

**Gap conocido**: `REGLAMENTO DE POSGRADOS DE LA UTE...2017.pdf` y `RESOLUCIÓN RECTORAL...INSTRUCTIVO POSGRADOS CCSS.pdf` no produjeron texto (son PDFs escaneados como imagen, sin capa de texto) — 0 chunks de esos dos. No afecta la demo de sílabos de pregrado; para incluirlos haría falta OCR, que queda como mejora futura, no bloquea nada ahora.

Para la demo de validación de sílabos de pregrado, el documento que más aporta es el **Reglamento de Régimen Académico**; el resto se indexa igual (corpus genérico, no se filtra a mano) para que el sistema cite la fuente correcta según el tipo de sílabo, y para que el corpus sea lo bastante grande como para justificar el paso de embeddings en el HPC.

## Búsqueda web de respaldo (no usada, por si hace falta una versión alterna)

Durante la sesión se buscaron también versiones públicas de la LOES y el Reglamento de Régimen Académico del CES en sus sitios oficiales (ces.gob.ec, repositorios universitarios públicos) antes de que el usuario compartiera su propia recopilación. Esas versiones no se descargaron ya que el usuario proveyó las suyas; quedan aquí registradas como alternativa si se necesita una fuente adicional:

- LOES — Consejo de Educación Superior / varios espejos institucionales (`.edu.ec`).
- Reglamento de Régimen Académico — ces.gob.ec (versión vigente desde sept. 2022, y una versión de mayo 2023).
