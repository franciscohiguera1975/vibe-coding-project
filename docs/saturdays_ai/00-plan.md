# Proyecto Saturdays AI Quito — Validación de sílabos con RAG

Registro vivo de decisiones y pasos. Se actualiza en cada avance (no es un documento final, es el log del proyecto).

## 1. Contexto y entregable

Proyecto para el Demo Day de Saturdays AI Quito (ver `DemoDay Sai 2026.pdf`), evaluado con la rúbrica de ese archivo: problema/relevancia (15%), calidad de la solución IA (20%), uso apropiado de ML/GenAI (15%), calidad técnica y arquitectura (15%), modelo evaluado con métricas (10%), deploy/producto funcional (10%), innovación (5%), demo y comunicación (10%).

Se reutiliza la Vibe Coding Platform (proyecto del curso CEDIA, mismo repositorio) como base: mismo backend, mismo frontend, mismo VPS. Esto es un requerimiento nuevo agregado a esa plataforma, no un proyecto aparte.

## 2. Alcance decidido (con el usuario, 2026-10-09)

**Se construye ahora:**
- Un motor de RAG genérico y compartido (ingestión de documentos → chunking → embeddings → recuperación → generación con cita de fuente).
- Caso de uso principal, el que se demuestra en vivo: **validación de sílabos contra la normativa de la UTE**, con hallazgos citando el artículo/documento exacto.
- Complemento al AI Tutor ya existente en la plataforma (fase de i18n/narración, ya desplegada): sus pistas y retroalimentación ahora se fundamentan (RAG) en el contenido real de las guías de práctica, en vez de depender solo del LLM.
- Proveedor de LLM y de embeddings para el RAG, configurable por variable de entorno (igual patrón que `AI_PROVIDER` ya existente para el tutor): **el HPC de CEDIA (vLLM + TEI, vía túnel) es el proveedor principal** — ver §5 más abajo para el porqué y el cambio de rumbo; GitHub Models (capa gratuita) queda como respaldo intercambiable sin tocar código, y Anthropic (ya integrado en el código, hoy inactivo) sigue disponible como alternativa futura.

**Próximos pasos (sección 8 de la rúbrica, no se construyen ahora):**
- Validación del distributivo de carga horaria docente.
- Informe de ejecución del distributivo.

**Descartado de este proyecto:** usar el "tutor sobre las guías" como caso principal de demo — se mantiene solo como mejora complementaria del tutor ya existente (ver arriba), no como pantalla nueva protagonista.

## 3. Hallazgo importante sobre Anthropic (aclarado 2026-10-09)

`AnthropicAdapter` existe en `apps/backend/app/infrastructure/ai/anthropic_adapter.py` e implementa el puerto `AIProvider` (pistas, feedback, análisis de imágenes del tutor). **No está activo**: tanto en local como en producción `AI_PROVIDER=mock`. No hay conflicto con agregar GitHub Models — se le da su propio ajuste independiente (`RAG_LLM_PROVIDER`), sin tocar `AI_PROVIDER`.

## 4. Corpus de normativa

El usuario recopiló los documentos reales (públicos/institucionales) en `docs/reglamentos_ute/` — ver detalle y rol de cada uno en [`01-corpus-normativa.md`](01-corpus-normativa.md). ~311 páginas en total entre 10 documentos.

## 5. Arquitectura (actualizada 2026-10-09 — decisión final tras varias iteraciones)

Cambio de rumbo respecto a la primera versión de este documento: el HPC **sí sirve tráfico en vivo** durante la demo (no solo un job de benchmark puntual), porque el usuario quiere demostrar el uso real del HPC y de embeddings como parte de los objetivos de aprendizaje del curso.

- **Embeddings y generación, ambos en el HPC**, cero dependencia de ML en el VPS:
  - **TEI** (Text Embeddings Inference, Hugging Face) sirve los embeddings — mismo modelo para indexar el corpus una vez y para cada consulta en vivo (tienen que ser el mismo espacio vectorial).
  - **vLLM** sirve la generación (el LLM de chat que redacta el veredicto de cumplimiento, citando el artículo).
  - Se decidió **dos servidores separados** (no uno combinado) a propósito: son herramientas estándar ya probadas; un servidor propio cargando dos modelos a la vez es más código sin probar y más riesgo para el día de la demo.
  - Ambos se tunelan al VPS con un solo comando `ssh -R` (túnel SSH inverso) — el HPC nunca necesita estar expuesto a internet. Detalle completo: [`02-hpc-pasos.md`](02-hpc-pasos.md).
  - **Esto no es "siempre disponible"**: la función de RAG solo funciona mientras la sesión `salloc` + el túnel están activos. Se levanta antes de la demo (12-15 min, día del Demo Day) — limitación conocida y honesta, documentada también en la sección 8 ("limitaciones actuales") de la presentación.
  - **Respaldo**: `RAG_LLM_PROVIDER` es una variable de entorno — si el túnel falla el día de la demo, se puede apuntar a GitHub Models (capa gratuita) sin tocar código, solo cambiando esa variable.
- **Vive en el mismo VPS** que ya corre la plataforma para todo lo demás: la UI, las pantallas nuevas, y ahora también el almacén de chunks+embeddings (ver el cambio de arquitectura más abajo). El VPS solo hace llamadas HTTP salientes a los dos puertos tunelados — nunca carga un modelo él mismo.
- **Chunks + embeddings de la normativa: tabla LanceDB embebida (cambio de arquitectura, 2026-10-09)**, no Postgres. Antes se guardaban en una columna JSONB de Postgres y la recuperación era fuerza bruta en Python sobre esa tabla (~900 filas, trivial para el volumen). Se decidió reemplazar ese almacenamiento por **LanceDB**, una base de datos vectorial embebida (corre en el mismo proceso que la consulta, como SQLite) — **decisión pedagógica deliberada, no una necesidad de escala**: el objetivo es que el proyecto demuestre el uso de un componente de base de datos vectorial dedicado como parte de los objetivos de aprendizaje del curso, no porque ~900 filas lo requieran (la razón de usarlo es la misma razón por la que se usan vLLM/TEI reales en vez de simularlos: aprender la herramienta de verdad).
  - **Por qué vive en el VPS y no en el HPC**: LanceDB es una librería embebida, no un servicio de red — debe correr co-ubicada con el proceso que la consulta (el backend FastAPI, en el VPS). El HPC solo aloja servicios alcanzables por red (vLLM para generación, TEI para calcular embeddings nuevos, ambos tunelados); la recuperación sobre vectores ya calculados es una operación local, síncrona y sin GPU — no tiene relación con la disponibilidad del túnel del HPC.
  - El algoritmo de recuperación (`app.domain.services.rag_retrieval`) sigue operando sobre lo que devuelve `list_all()` del repositorio, ahora respaldado por LanceDB en vez de Postgres. El cambio de almacenamiento queda contenido a la capa de infraestructura (`LanceDbNormativaChunkRepository`, detrás del mismo `NormativaChunkRepository` Protocol) — nada en el dominio, los casos de uso, los routers, ni el frontend necesitó cambios. **Nota (2026-10-10, ver §9)**: ese algoritmo dejó de ser solo similitud de coseno — ahora es una recuperación híbrida (coseno + BM25 por palabra clave, fusionados con Reciprocal Rank Fusion), descrita en detalle en la sección 9.
  - `rag_evaluation_runs` (los resultados persistidos de las corridas de evaluación baseline-vs-RAG) **se queda en Postgres sin cambios** — solo se movieron los chunks+embeddings, no los resultados de evaluación.
  - Migración `73b590c68190` elimina la tabla `normativa_chunks` de Postgres (ya no se usa); settings nuevo `LANCEDB_PATH` (default `./storage/lancedb`, mismo patrón que `STORAGE_LOCAL_PATH`).
- Sin esto (reflejado también en `02-hpc-pasos.md` §7): el día de la demo hay que reservar el HPC, levantar ambos servidores y el túnel ANTES de empezar — no es instantáneo, hay que dejar margen.

## 6. Pantallas nuevas en la plataforma

- **Validación de sílabos**: subir/pegar un sílabo, ver el reporte de cumplimiento con citas a la normativa.
- **Evaluación**: tabla comparando el caso base (sin RAG) contra el caso con RAG, sobre el set de ~15 preguntas de evaluación — esta pantalla es, en vivo, la sección "Resultados" de la rúbrica.
- Nueva entrada de menú para acceder a ambas (nivel de "Presentación"/"Catálogo" en el header).

## 7. Estado actual / próximos pasos inmediatos

- [x] Rúbrica y alcance acordados con el usuario.
- [x] Confirmado que Anthropic está inactivo (sin conflicto).
- [x] Corpus de normativa localizado e inventariado (`docs/reglamentos_ute/`, ver `01-corpus-normativa.md`).
- [x] Extraer y trocear (chunk) el texto de los 10 PDFs → 896 chunks (`apps/backend/scripts/rag/ingest_normativa.py`, salida en `apps/backend/scripts/rag/data/chunks.jsonl`, no versionado — dato local).
- [x] Diseñar la tabla de chunks+embeddings y la migración.
- [x] Elegir y configurar el modelo de embeddings (mock para dev/test; TEI/HPC configurable via `EMBEDDING_PROVIDER`) y el adaptador GitHub Models (via `RAG_LLM_PROVIDER=openai_compatible`, cualquier endpoint compatible con OpenAI).
- [x] Construir el caso de uso de validación de sílabos + endpoint.
- [x] Construir las 2 pantallas nuevas + entrada de menú.
- [x] Escribir el set de evaluación (15 preguntas/casos) y la comparación baseline vs RAG.
- [ ] Ejecutar los pasos del HPC (`02-hpc-pasos.md`) y volcar sus resultados aquí. **Pendiente**: requiere que el usuario reserve el HPC y levante el túnel (ver §7 de ese documento); todo el código ya soporta `RAG_LLM_PROVIDER=openai_compatible` / `EMBEDDING_PROVIDER=tei` sin cambios adicionales.
- [x] Reforzar el AI Tutor existente con el mismo motor de RAG (grounding opcional y a prueba de fallos en `GenerateAIHintUseCase`).

## 8. Fase de implementación — resultados (2026-10-09)

Resumen de lo construido en esta fase, para referencia rápida del propietario del proyecto. Todo lo listado abajo corre en modo `mock` (cero red real) salvo que se indique lo contrario; cambiar a HPC real es solo cuestión de variables de entorno (`RAG_LLM_PROVIDER=openai_compatible`, `EMBEDDING_PROVIDER=tei`, `RAG_BASE_URL`, `EMBEDDING_BASE_URL`), sin tocar código.

### Backend — ya existía antes de esta fase (ver prompt de arranque)

- `app/application/ports/rag.py` (`EmbeddingPort`, `RagPort`), `app/infrastructure/ai/mock_rag_adapter.py`, `app/infrastructure/ai/openai_compatible_rag_adapter.py`, `app/infrastructure/ai/tei_embedding_adapter.py`.
- `app/domain/entities/rag.py`, `app/domain/repositories/rag_repository.py`, `app/domain/services/rag_retrieval.py`, `app/domain/services/syllabus_checklist.py` (ya completo: checklist de 5 items anclado en Art. 67 del Reglamento de Régimen Académico y Art. 40 del Reglamento del Estudiante).
- `app/infrastructure/database/models/rag.py`, `app/infrastructure/database/repositories/rag_repository.py`, `alembic/versions/b4d2e8a1f6c3_add_rag_tables.py` (migración, no aplicada aún al iniciar esta fase).
- `app/application/ports/unit_of_work.py` / `app/infrastructure/database/unit_of_work.py` (ya cableados con `normativa_chunks` y `rag_evaluation_runs`).
- `apps/backend/scripts/rag/ingest_normativa.py` + `apps/backend/scripts/rag/data/chunks.jsonl` (896 chunks, dato local gitignored).
- `.env.example` y `app/infrastructure/config.py` (settings `rag_llm_provider`, `embedding_provider`, etc., ya con `mock` como default).

### Backend — agregado en esta fase

- **Migración aplicada** a la base de desarrollo: `alembic upgrade head` corrió limpio (`a3c1f9b2d7e4` → `b4d2e8a1f6c3`), confirmado con `alembic current`.
- `app/interfaces/http/dependencies/rag.py` — factory `get_rag_port`/`get_embedding_port` (mock vs. TEI/OpenAI-compatible), espejando `dependencies/narration.py`.
- `app/interfaces/http/dependencies/rag_use_cases.py` — DI de los dos casos de uso nuevos.
- `apps/backend/scripts/rag/load_chunks.py` — script idempotente que calcula embeddings (via el `EmbeddingPort` configurado) y hace upsert en `normativa_chunks`, saltando chunks que ya tienen embedding. Ejecutado contra la base de desarrollo: 896/896 embebidos la primera vez, 0/896 en la segunda corrida (idempotencia verificada).
- `app/application/use_cases/rag/validate_syllabus.py` — **Caso de uso A**: por cada item del checklist, recupera top-3 chunks (RAG) y pide al LLM un veredicto `CUMPLE`/`NO_CUMPLE`/`NO_DETERMINADO` citando articulo+documento; degrada a la detección heurística por palabra clave si el LLM no sigue el formato (siempre ocurre en modo mock).
- `app/application/use_cases/rag/run_evaluation.py` — **Caso de uso C**: corre las 15 preguntas de `eval_set.jsonl` por baseline (sin RAG) y RAG (top-3 + generación grounded), puntuando si el chunk recuperado coincide con la cita esperada; persiste el resultado via `RagEvaluationRunRepository`.
- `apps/backend/scripts/rag/data/eval_set.jsonl` — **15 preguntas reales** (no gitignored, ver §9 abajo para el listado completo), ancladas en chunks reales de `chunks.jsonl`.
- `app/application/use_cases/ai/generate_hint.py` — **Caso de uso B**: agregado un parámetro opcional `embedding_port` (default `None`, retrocompatible). Si se provee, recupera 2 chunks de `normativa_chunks` relacionados con la práctica y los agrega como contexto adicional al prompt de la pista; cualquier fallo (proveedor roto, tabla vacía) se atrapa y se degrada en silencio al comportamiento exacto de antes. Cableado en `dependencies/ai_use_cases.py` con el mismo `get_embedding_port`.
- `app/interfaces/http/schemas/rag.py`, `app/interfaces/http/routers/rag.py` — 3 endpoints: `POST /api/rag/validate-syllabus` (autenticado), `POST /api/rag/evaluation/run` (permiso `practice:update`), `GET /api/rag/evaluation` (404 si no hay corridas aún). Registrados en `app/main.py`.
- `tests/conftest.py` — `normativa_chunks` y `rag_evaluation_runs` agregados a `TRUNCATE_TABLES`.
- `.gitignore` — excepción explícita para que `scripts/rag/data/eval_set.jsonl` sí se versione (el resto de `scripts/rag/data/` sigue gitignored).
- Pruebas nuevas (todas con `MockRagAdapter`, cero red real): `tests/unit/test_rag_retrieval.py` (5), `tests/integration/test_rag_use_cases.py` (4: validación con citas, validación sin chunks cargados, scoring de evaluación con fixture controlada, permiso requerido), `tests/integration/test_load_chunks_script.py` (1: idempotencia con un `EmbeddingPort` espía que cuenta llamadas a `embed()`), `tests/api/test_rag_api.py` (4: auth requerida, 5 items de checklist, permiso del endpoint de evaluación, 404→200 del `GET /api/rag/evaluation`), y 1 test ampliado en `tests/integration/test_ai_use_cases.py` (grounding aditivo + fallback silencioso ante fallo del `EmbeddingPort`).

### Frontend — agregado en esta fase

- `src/domain/entities/rag.ts`, `src/application/services/rag-service.ts`, `src/application/hooks/use-rag.ts`, cableado en `src/infrastructure/container.ts` (mismo patrón que `practice-service`/`use-practices`).
- `src/presentation/pages/public/SyllabusValidationPage.tsx` — textarea + envío + 5 tarjetas de resultado con badge Cumple/No cumple/No determinado, explicación y citas.
- `src/presentation/pages/public/RagEvaluationPage.tsx` — botón "Ejecutar evaluación" (gateado por el permiso `practice:update`, mismo que el backend), tarjetas de estadísticas, oración resumen, y tabla de 15 filas (pregunta, cita esperada, respuesta baseline con ✓/✗, respuesta RAG con ✓/✗).
- `src/App.tsx` — rutas `/validacion-silabos` (dentro de `ProtectedRoute`, requiere sesión) y `/evaluacion-rag` (pública, igual que la pantalla de evaluación no expone datos sensibles).
- `src/presentation/layout/Header.tsx` — UNA entrada de nivel superior ("VALIDACIÓN RAG") con un submenú desplegable (hover/click) a las dos pantallas; replicado en el menú móvil.
- i18n: 33 keys nuevas por idioma bajo `header.nav.{rag,syllabusValidation,ragEvaluation}`, `syllabusValidationPage.*`, `ragEvaluationPage.*`, traducidas (no machine-garbage) a es/en/pt/fr. Paridad de claves verificada programáticamente (script Node): **365 keys idénticas en los 4 locales**.

### Verificación end-to-end (navegador, modo mock)

Se levantaron ambos servidores de desarrollo (`uvicorn` + `vite`) y se probó manualmente con el usuario admin sembrado: login → dropdown "VALIDACIÓN RAG" → **Validación de sílabos** (textarea → 5 tarjetas con citas reales del corpus) → **Evaluación** (botón "Ejecutar evaluación" → tabla de 15 filas + tarjetas de stats). Todo funcional. Nota esperada: en modo `mock` los embeddings son pseudo-aleatorios (hash del texto), así que las citas recuperadas no son semánticamente relevantes y el score RAG vs. baseline da 0/15 en ambos — eso es correcto para `mock` y **no** indica un bug; con TEI/HPC real (embeddings semánticos de verdad) se espera que el score RAG suba significativamente por encima de 0, que es justamente lo que la pantalla de Evaluación está pensada para demostrar en vivo.

### Pruebas — resultado final

- **Backend (pytest)**: 110 passed, 2 failed (preexistentes, no relacionados con RAG — `tests/api/test_practice_narration_api.py`, fallan porque `.env` tiene `NARRATION_PROVIDER=elevenlabs` sin `ELEVENLABS_API_KEY`; mismo resultado antes y después de esta fase). Total subió de 97 a 112 tests (15 nuevos + 1 ampliado).
- **Frontend**: `npx tsc -b` sin errores; `npx vitest run` → 6 archivos, 19 passed (sin cambios, ninguna prueba existente se rompió).
- **Cero llamadas de red reales**: confirmado por diseño (`MockRagAdapter` en todos los tests y en el `.env` de desarrollo, que no fija `RAG_LLM_PROVIDER`/`EMBEDDING_PROVIDER`, por lo que usan el default `mock`) y por inspección de cada adaptador real (`OpenAICompatibleRagAdapter`, `TeiEmbeddingAdapter`), que nunca se instancian salvo que el usuario cambie esas variables explícitamente.

### Cambio de arquitectura — chunks+embeddings de Postgres a LanceDB (2026-10-09)

Entrada posterior del log: la tabla `normativa_chunks` descrita arriba (Postgres JSONB + fuerza bruta en Python) se reemplazó por una tabla **LanceDB** embebida. Ver §5 para el razonamiento completo (decisión pedagógica deliberada — demostrar un componente de base de datos vectorial dedicado, no una necesidad de escala — y por qué vive en el VPS y no en el HPC). Resumen de lo cambiado:

- `app/infrastructure/database/lancedb_chunk_repository.py` (nuevo) — `LanceDbNormativaChunkRepository`, implementa exactamente el mismo `NormativaChunkRepository` Protocol (sin cambios en su firma). `SqlAlchemyNormativaChunkRepository` y `NormativaChunkModel` se eliminaron (ya no hace falta un modelo SQLAlchemy para esto).
- `app/infrastructure/config.py` / `.env.example` — nuevo setting `lancedb_path` / `LANCEDB_PATH` (default `./storage/lancedb`, mismo patrón que `storage_local_path`).
- `app/infrastructure/database/unit_of_work.py` — `self.normativa_chunks` ahora es un `LanceDbNormativaChunkRepository(lancedb_path)` en vez de `SqlAlchemyNormativaChunkRepository(session)`; `self.rag_evaluation_runs` **no cambió** (se queda en Postgres).
- `alembic/versions/73b590c68190_...py` (nueva migración, encadenada tras `b4d2e8a1f6c3`) — elimina la tabla `normativa_chunks` de Postgres (ya no se usa); `rag_evaluation_runs` no se toca. Aplicada limpio a la base de desarrollo (`alembic current` → `73b590c68190`).
- `tests/conftest.py` — `normativa_chunks` se quitó de `TRUNCATE_TABLES` (la tabla ya no existe en Postgres); se agregó aislamiento equivalente para LanceDB (`LANCEDB_PATH` apunta a un directorio temporal exclusivo de la sesión de pruebas, fijado antes de importar cualquier módulo de `app`, y se borra/recrea antes de cada test — mismo rol que el `TRUNCATE TABLE` de Postgres, pero a nivel de directorio).
- **Nada en el dominio, casos de uso, routers o frontend cambió**: `rag_retrieval.py`, `validate_syllabus.py`, `run_evaluation.py`, `generate_hint.py`, el router `rag.py` y toda la UI siguen funcionando sin tocar, porque solo dependían de `NormativaChunkRepository.list_all()`/`upsert()`/`get_by_chunk_id()`/`count()` — nunca de Postgres directamente. La recuperación semántica sigue siendo la misma fuerza bruta en Python sobre lo que devuelve `list_all()`; LanceDB no se usa (a propósito) para hacer la búsqueda vectorial nativa, para mantener el cambio contenido a la capa de infraestructura.
- Verificado end-to-end: `scripts/rag/load_chunks.py` corrido contra LanceDB real (modo mock) → 896/896 embebidos la primera vez, 0/896 en la segunda corrida (idempotencia verificada, igual que antes con Postgres). Suite completa de pytest: 112 passed (mismo número que antes del cambio, cero regresiones). Frontend sin tocar: `tsc -b` limpio, `vitest run` 19/19.

### Las 15 preguntas del set de evaluación (`scripts/rag/data/eval_set.jsonl`)

Para que el propietario del proyecto pueda revisar la calidad del grounding antes de la demo. 12/15 ancladas en los artículos de evaluación/sílabo del Reglamento de Régimen Académico y el Reglamento del Estudiante (el caso de uso principal); 3/15 de otros documentos del corpus, para variedad.

1. **(Art. 67, Reglamento de Régimen Académico)** ¿Qué elementos deben definir y difundir los docentes a los estudiantes a través del sílabo?
2. **(Art. 40, Reglamento del Estudiante)** ¿En qué casos puede un estudiante de la UTE solicitar la recalificación de un examen o evaluación?
3. **(Art. 35, Reglamento del Estudiante)** ¿Qué principios debe garantizar el sistema interno de evaluación estudiantil de la UTE?
4. **(Art. 36, Reglamento del Estudiante)** ¿Cómo se clasifican los tipos de evaluación de los aprendizajes en la Universidad UTE?
5. **(Art. 37, Reglamento del Estudiante)** ¿Cuál es la escala de calificación y el promedio mínimo para aprobar una asignatura en la UTE?
6. **(Art. 38, Reglamento del Estudiante)** ¿Quiénes tienen derecho a rendir la evaluación remedial en la UTE y qué efecto tiene en la calificación final?
7. **(Art. 41, Reglamento del Estudiante)** ¿Qué debe hacer el director de carrera si un docente no registra oportunamente las calificaciones de una asignatura?
8. **(Art. 42, Reglamento del Estudiante)** ¿Qué porcentaje mínimo de asistencia necesita un estudiante de la UTE para no reprobar una asignatura por inasistencia?
9. **(Art. 66, Reglamento de Régimen Académico)** ¿Qué debe garantizar el sistema interno de evaluación estudiantil, y con qué frecuencia mínima se aplican las evaluaciones formativa y sumativa?
10. **(Art. 68, Reglamento de Régimen Académico)** ¿Qué debe hacer una IES cuando un estudiante con necesidades educativas requiere adaptaciones curriculares en su evaluación?
11. **(Art. 70, Reglamento de Régimen Académico)** ¿Qué es la matrícula según el Reglamento de Régimen Académico?
12. **(Art. 71, Reglamento de Régimen Académico)** ¿Qué tipos de matrícula existen según el Reglamento de Régimen Académico?
13. **(Art. 1, Instructivo Segunda Lengua)** ¿A quiénes aplica el Instructivo de Segunda Lengua de la UTE?
14. **(Art. 3, Instructivo Segunda Lengua)** ¿Qué se entiende por "suficiencia de una segunda lengua" según el Instructivo de Segunda Lengua?
15. **(Art. 1, LOES 2025)** ¿Qué regula la Ley Orgánica de Educación Superior (LOES) según su artículo 1?

### Pendiente real para el día de la demo

- Ejecutar `02-hpc-pasos.md` (reservar GPU, levantar vLLM+TEI, túnel SSH, `RAG_LLM_PROVIDER=openai_compatible`/`EMBEDDING_PROVIDER=tei` en el `.env` de producción) y volver a correr `scripts/rag/load_chunks.py` contra el VPS para recalcular embeddings reales (los embeddings mock no son compatibles con TEI — distinto espacio vectorial).
- Correr `POST /api/rag/evaluation/run` de nuevo una vez el HPC esté arriba, para tener un número real de "RAG acertó N/15" que mostrar en la diapositiva de resultados (ahora mismo el run persistido es el de modo mock, 0/15 en ambos, solo para fines de desarrollo).

## 9. Recuperación híbrida — BM25 + vectorial + RRF (2026-10-10)

Se generó un informe (.docx) y una presentación (.pptx) detallados para el DemoDay (`docs/saturdays_ai/`, entregados al usuario fuera del repo, no versionados aquí). A partir de ahí el usuario preguntó si convenía adoptar un esquema de recuperación híbrida (BM25 + búsqueda vectorial + Reciprocal Rank Fusion), con la intención explícita de que este prototipo sirva de base real para el futuro proyecto institucional de la UTE, no solo para la demo. Se decidió implementarlo ya, antes del Demo Day.

**Qué cambió**: `app/domain/services/rag_retrieval.py` dejó de ser solo coseno — ahora `retrieve_top_k(query_embedding, query_text, chunks, *, k=3)` calcula dos rankings independientes sobre el mismo subconjunto de chunks (los que ya tienen embedding cargado) y los fusiona:

- **Ranking vectorial**: coseno sobre `query_embedding`, igual que antes.
- **Ranking BM25**: `rank-bm25` (`BM25Okapi`, nueva dependencia, puro Python, sin servidor aparte — coherente con la decisión ya tomada de no usar infraestructura de búsqueda pesada) sobre el texto crudo de los chunks, tokenizado con una regex simple (minúsculas, letras/dígitos, soporta tildes y eñe).
- **Fusión (RRF)**: `score(chunk) = Σ 1 / (60 + rank)` sobre los rankings donde aparece (rank 1-indexado) — la misma constante (`k=60`) que usan Elasticsearch/OpenSearch por defecto, no un valor ajustado a mano. `RetrievedChunk.score` pasa a ser ese score RRF, no el coseno crudo.

**Por qué**: la búsqueda puramente vectorial puede fallar cuando la consulta y la normativa comparten una palabra exacta (p. ej. "calificación", "asistencia") pero el embedding no la recupera entre el top-k por razones semánticas no evidentes; BM25 la recupera por coincidencia léxica exacta, y RRF deja que ambas señales se refuercen sin que una domine a la otra por escala (BM25 no está acotado, coseno sí).

**Dónde se propagó**: los 3 llamadores de `retrieve_top_k` (`ValidateSyllabusUseCase`, `RunRagEvaluationUseCase`, `GenerateAIHintUseCase._retrieve_grounding`) ya tenían el texto de la consulta disponible antes de calcular el embedding — se les pasó ese mismo texto, sin cambiar ninguna otra firma ni los puertos (`EmbeddingPort`/`RagPort` no se tocaron).

**Verificación**: `tests/unit/test_rag_retrieval.py` reescrito (nueva firma + un test que confirma que un chunk con coincidencia léxica exacta pero embedding lejano entra al top-k gracias a BM25, algo que el ranking puramente vectorial anterior no garantizaba). Suite completa: **118 passed** (antes 116; +2 netos), `ruff check` limpio. Nada en los routers, schemas o frontend cambió — la fusión es interna a la capa de dominio.

**Optimización (mismo día)**: el índice BM25 se estaba reconstruyendo en cada sub-consulta (5 veces por sílabo validado, 15 veces por corrida de evaluación) — costo innecesario de CPU en el VPS pequeño que sirve el resto de la plataforma. Se agregó `build_bm25_index(chunks)` + parámetro opcional `bm25_index` en `retrieve_top_k`, para construirlo una sola vez por ejecución y reutilizarlo en las sub-consultas (`ValidateSyllabusUseCase.execute`, `RunRagEvaluationUseCase.execute`). De paso se protegió `Bm25Index` contra `ZeroDivisionError` cuando aún no hay chunks cargados (BM25Okapi no acepta un corpus vacío). Suite completa re-verificada: 118 passed.

Desplegado a producción: commit `24c45ec` (`feat(rag): add hybrid retrieval (BM25 + vector + RRF)`).

**Entregables del DemoDay actualizados**: el informe (.docx) y la presentación (.pptx) se regeneraron para describir la arquitectura de recuperación híbrida (en vez de "solo vectorial"), y se aplicó la convención de explicar cada sigla (RAG, HPC, LLM, API, VPS, GPU, BM25, RRF, etc.) entre paréntesis la primera vez que aparece en cada documento. Copiados a `docs/saturdays_ai/` con nombres propios del proyecto (`DemoDaySaturdaysAI_HybridRetrieval_Informe.docx` / `..._Presentacion.pptx`, sin el prefijo `VC-2026-008-038` que corresponde al OTRO curso, Vibe Coding CEDIA).

## 10. Embeddings de producción recargados con el fix de prefijos (2026-10-10/11)

Con el usuario confirmando explícitamente el borrado (acción destructiva, bloqueada una vez por el clasificador de Claude Code hasta tener esa confirmación): se verificó primero el estado real de los túneles del HPC desde el VPS — **TEI (8766) vivo** (HTTP 200), **vLLM (8765) caído** (`Connection reset by peer`: el socket del túnel SSH seguía abierto en el VPS, pero el lado del HPC ya no respondía — la reserva/sesión de esa parte había terminado).

Como la recarga de embeddings solo depende de TEI, se procedió con esa parte:

1. Se usó `db.drop_table('normativa_chunks')` (API propia de LanceDB, no un `rm -rf` de todo el directorio) para vaciar la tabla sin tocar el resto de `storage/lancedb/` — confirmado `chunks.jsonl` (fuente, 896 líneas) intacto antes de borrar.
2. `scripts/rag/load_chunks.py` recalculó los 896 embeddings contra TEI real: `896 embebidos, 0 ya existían (total 896), en 463.1s` — el "0 ya existían" confirma que partió de cero, no que reusó los viejos.
3. **Verificación de calidad** (script ad-hoc contra producción, usando exactamente `TeiEmbeddingAdapter` + `retrieve_top_k` + `build_bm25_index`, el mismo código que usa `RunRagEvaluationUseCase`): las 15 preguntas de `eval_set.jsonl` recuperan ahora el artículo/documento esperado entre el top-3 — **15/15**. Antes del fix, el sistema citaba siempre el mismo documento irrelevante sin importar la pregunta.

**Dato clave para la cifra de la rúbrica**: `rag_citation_match` (lo que persiste `RunRagEvaluationUseCase` como "aciertos RAG") depende solo de la recuperación (embeddings + BM25 + RRF), no de `vLLM` — `vLLM` solo redacta el texto de la respuesta que se ve en pantalla, no afecta este conteo. Por eso el **15/15** ya es la cifra real y reproducible, aunque `vLLM` siga caído.

**Pendiente real, ahora acotado solo a esto**: correr el endpoint oficial `POST /api/rag/evaluation/run` (no el script ad-hoc) una vez `vLLM` esté arriba de nuevo, para que (a) quede oficialmente persistido en `rag_evaluation_runs` y (b) la pantalla "Evaluación" de la plataforma muestre el resultado real en vivo durante la demo — se espera que confirme el mismo 15/15, más las respuestas en lenguaje natural generadas por `vLLM`. El usuario está reintentando levantar `vLLM` (el arranque es lento — `import torch` tarda varios minutos en un job/contenedor recién creado, consistente con lo ya documentado en `02-hpc-pasos.md`).

## 11. vLLM lento por contención real del nodo HPC, y corrida oficial de evaluación (2026-10-11)

`vLLM` tardó más de 10 minutos sin arrancar (sin error) en el job 29189/`compute-0-1`. Diagnóstico en vivo (`top`, `nvidia-smi`, pedidos por Claude Code, ejecutados por el usuario): `load average` de ~87 en `compute-0-1`, causado por trabajos **de otros usuarios** (GROMACS, entrenamientos de ML) con cientos de horas acumuladas — nada que ver con la reserva del usuario. `nvidia-smi` confirmó que `vLLM` ni siquiera había tocado la GPU todavía (0% uso, solo TEI con 1.5GB). `sinfo -N -o "%N %C %O" -p gpu-dev` mostró `compute-0-2` con 192 CPUs libres de 256 (carga 26) contra solo 56 libres en `compute-0-1` (carga 87). Se canceló el job y se volvió a reservar con `--nodelist=compute-0-2`; ahí `vLLM` y TEI arrancaron en tiempo normal.

**Corrida oficial**: con ambos túneles confirmados (`curl` desde el VPS: HTTP 200 en los dos), se intentó primero `POST /api/rag/evaluation/run` vía la API pública — **504 Gateway Timeout**. Causa raíz encontrada: `gunicorn` corre con su timeout de worker por defecto (**30 segundos**, nunca configurado explícitamente en el `.service` de producción) — el endpoint, al llamar a `vLLM` real 30 veces (15 preguntas × baseline + RAG), tarda varios minutos, así que el worker se mataba a medio proceso sin dejar ningún registro (ni en `rag_evaluation_runs` ni en los logs). **Corregido en producción**: se agregó `--timeout 300` al `ExecStart` de `/etc/systemd/system/vibe-coding-platform-api.service` (`systemctl daemon-reload` + `restart`), y se documentó en `docs/native-deployment.md` para que sobreviva a una reinstalación futura — el workflow de deploy (`deploy.yml`) no toca el `.service`, así que este fix persiste solo mientras no se reinstale el servicio desde cero.

Con el timeout corregido, se corrió el caso de uso directamente en el servidor (script puntual invocando `RunRagEvaluationUseCase` con los adaptadores reales, para no depender de que la primera corrida larga pasara por gunicorn/nginx mientras se verificaba el fix) — **resultado oficial, persistido en `rag_evaluation_runs`**:

```
{'total': 15, 'rag_citation_matches': 15, 'baseline_citation_matches': 0}
```

**15/15 con RAG, 0/15 con baseline.** Confirmado también cualitativamente: el baseline alucina (p. ej., para la pregunta sobre contenido obligatorio del sílabo, inventa el "Artículo 35" y cita una universidad inexistente, "Universidad Tecnológica de El Salvador"); el RAG cita el Artículo 67 real del Reglamento de Régimen Académico con el texto exacto de la normativa. Visible ahora en vivo en la pantalla "Evaluación" de la plataforma (`GET /api/rag/evaluation`, verificado con `curl` autenticado).

Informe (.docx) y presentación (.pptx) actualizados con esta cifra real (reemplazando los 3 placeholders "pendiente" que quedaban en cada documento) y con el ejemplo cualitativo del baseline alucinando — commit `c64fa33`.

**Ya no queda ningún pendiente bloqueante para el Demo Day** más allá de la validación cualitativa con usuarios reales (coordinadores de carrera), documentada como "próximos pasos", no como bloqueo.

## 12. AI Tutor conectado al HPC + arquitectura de 3 servicios/2 GPUs + modelo de texto subido a 14B (2026-10-11)

Cambio grande: el AI Tutor ("Preguntar al tutor IA") dejó de estar en `mock` y ahora usa cómputo real del HPC, igual que el RAG — y de paso el RAG subió su modelo de generación de 7B a 14B.

**Código nuevo** (`AIProvider`, el puerto del tutor, independiente de `RagPort` — ver §3/§5): `OpenAICompatibleAiAdapter` (`app/infrastructure/ai/openai_compatible_ai_adapter.py`), implementa `generate_text`/`generate_feedback` contra un vLLM (igual patrón que `OpenAICompatibleRagAdapter`) y `analyze_image` contra un **modelo con visión separado** (`AI_VISION_BASE_URL`/`AI_VISION_MODEL`), con el formato de mensajes de visión de OpenAI (`image_url` + base64). Nuevo valor `AI_PROVIDER=openai_compatible`. Commit `099d4fe`.

**Arquitectura HPC, de 2 a 3 servicios**: se agregó un segundo vLLM con un modelo de visión-lenguaje (`Qwen2.5-VL-7B-Instruct`, sirve texto Y análisis de imagen para el tutor — un modelo VL no pierde capacidad de texto puro) en una **segunda GPU**, aislado del vLLM del RAG. Esto obligó a pasar de 1 a 2 GPUs por reserva, lo que destapó dos descubrimientos reales de la cuenta/clúster:
- **`gpu-dev` solo permite 1 GPU por job** (`QOSMaxGRESPerJob`) — hubo que cambiar a la partición **`gpu`** (mismos nodos físicos, otra QOS, hasta 2 GPUs y `cpu=160` por job). Diagnosticado con `sacctmgr show qos format=Name,MaxTRESPerJob%40`, ahora documentado en `02-hpc-pasos.md` §9 con la tabla completa de límites por partición.
- **`CUDA_VISIBLE_DEVICES=N` como prefijo de shell no funciona con enroot** — los contenedores no heredan variables de entorno del shell (mismo motivo que el fix de `HF_ENDPOINT` para TEI, semanas atrás). Hay que pasarlo como `--env CUDA_VISIBLE_DEVICES=N`, flag de `enroot start`. Sin el fix, los dos vLLM terminaban compartiendo la misma GPU física sin ningún aviso — con modelos chicos (7B+7B) cabían juntos por accidente; con el de texto ya en 14B, ya no cupieron y reventó con un error real de memoria (`ValueError: Free memory on device cuda:0 ... less than desired`), que fue como se descubrió el bug.

**Modelo de texto del RAG subido a `Qwen/Qwen2.5-14B-Instruct`** (antes 7B, 29.6GB vs 14.19GB) — pedido explícito del usuario, aprovechando que ahora cada vLLM vive aislado en su propia GPU de 40GB. Re-verificado con la corrida oficial de evaluación tras el cambio:

```
{'total': 15, 'rag_citation_matches': 15, 'baseline_citation_matches': 1}
```

Mismo 15/15 (la métrica depende solo de recuperación, no del modelo de generación — esperado). Revisado además el texto real de una respuesta: formato más limpio (lista de elementos en vez de prosa continua), misma cita correcta (Art. 67) — sin regresión, posible mejora cualitativa. `RAG_CHAT_MODEL=Qwen/Qwen2.5-14B-Instruct` agregado al `.env` de producción, servicio reiniciado.

**Activado en producción y verificado en vivo**: `AI_PROVIDER=openai_compatible`, `AI_BASE_URL`/`AI_VISION_BASE_URL=http://localhost:8767/v1`, `AI_MODEL`/`AI_VISION_MODEL=Qwen/Qwen2.5-VL-7B-Instruct` (mismo modelo de visión para texto e imagen del tutor, puerto 8767 — el del RAG, 8765, no se tocó). `POST /api/ai/hint` probado contra una práctica real (`image-02-diagnostico-errores`): respuesta pedagógica real y específica ("compara los conteos... verifica iluminación, superposición, desenfoque..."), ya no la respuesta simulada del mock. Falta probar `analyze_image` (necesita subir una imagen real, no solo JSON) — pendiente, no bloqueante.

**Reflejado en los entregables** (ver §14): informe y presentación ya actualizados con el modelo de 14B, la arquitectura de 2 GPUs/3 servicios y el AI Tutor conectado al HPC.

## 13. Tercera pantalla — chat de consultas sobre normativa (2026-10-11)

Nueva pantalla en el menú "Validación RAG" (junto a Validación de sílabos y Evaluación): un chat de preguntas libres sobre normativa académica. `ChatNormativaUseCase` reutiliza la misma recuperación híbrida (BM25 + vectorial + RRF) que `ValidateSyllabusUseCase`, pero sin checklist fijo — una pregunta, una respuesta, sin memoria de conversación. A diferencia del checklist (donde un `NO_DETERMINADO` es correcto y deseado), aquí el system prompt permite que el LLM responda con conocimiento general cuando la normativa indexada no cubre el tema, marcándolo explícitamente como no verificado — inspirado en el skill de la guía 24 de CEDIA (chatbot/tutor de curso) en cuanto a mostrar siempre los fragmentos recuperados antes de confiar en la respuesta, pero con una política más permisiva que la de esa guía (que nunca sale del material autorizado) porque este caso de uso sí necesita poder responder preguntas generales de educación superior.

`POST /api/rag/chat`, página `/chat-normativa`, 130 pruebas backend (4 nuevas), 394 claves i18n (paridad verificada en los 4 idiomas). Probado en el navegador (mock) y en producción con el modelo real de 14B — ejemplo real: pregunta sobre inasistencia, respuesta cita correctamente el Art. 42 del Reglamento del Estudiante (70% de asistencia mínima) y razona con precisión sobre por qué la normativa habla en porcentaje y no en número de faltas. Commit `ab5291d`.

## 14. Informe y presentación puestos al día + preguntas de ejemplo para la demo (2026-10-11)

El usuario preguntó explícitamente si el mecanismo del RAG (explicado paso a paso en el chat) y todo lo del §12/§13 ya estaban reflejados en los entregables — no lo estaban del todo, así que se actualizaron ambos documentos (editados a mano vía XML crudo, mismo procedimiento ya usado antes en este proyecto, porque el script original de generación con `docx-js`/`build_deck.js` ya no existe en el entorno de esta sesión):

**`DemoDaySaturdaysAI_HybridRetrieval_Informe.docx`**:
- Nueva subsección "Mecanismo paso a paso (lo que pasa en cada consulta)" en la sección 2 — los 8 pasos exactos explicados al usuario (TEI solo convierte texto a vector, nunca busca; LanceDB solo almacena, la búsqueda coseno+BM25+RRF es Python puro en el VPS).
- Modelo de generación actualizado a 14B en las 4 menciones (puerto `RagPort`, tabla de modelos, justificación de elección, tabla de capas).
- Nueva fila en la tabla de modelos: "Tutor IA (texto + imagen) · Qwen/Qwen2.5-VL-7B-Instruct · HPC CEDIA — GPU dedicada (nuevo, 2026-10-11)"; el párrafo introductorio pasó de "dos modelos" a "tres modelos".
- Nueva bala en "Demo funcional" mencionando la pantalla de Chat de normativa.
- Sección 6 (túneles SSH): de "dos túneles" a "3 túneles SSH inversos... repartido en 2 GPUs"; nueva fila en la tabla de capas para el vLLM de visión.
- Validado con `scripts/office/validate.py` (XSD + diff contra el original) tras corregir dos errores de XML mal balanceado introducidos durante la edición a mano (un `</w:p>` de más y, el real causante, un `</w:p>` de menos que se había tragado el cierre del párrafo anterior a la nueva subsección) — lección: tras cada inserción de párrafos nuevos hay que contar aperturas/cierres de `<w:p>` explícitamente, no solo verificar que el anchor se reemplazó una vez.

**`DemoDaySaturdaysAI_HybridRetrieval_Presentacion.pptx`**: dado que el entorno no permite render visual (LibreOffice confirmado roto), se descartó agregar una tercera caja nueva al diagrama de arquitectura de la diapositiva 5 (cálculo mostró que no sobra espacio vertical sin reposicionar todo el layout, riesgo alto sin poder verificar visualmente) y en su lugar se hicieron solo ediciones de texto dentro de cajas/tablas ya existentes, verificando antes que el texto nuevo cabe en el espacio ya disponible de cada caja (conteo de caracteres vs. alto declarado):
- Diapositiva 5: `vLLM · Qwen2.5-7B-Instruct` → 14B; `inverso ×2` → `×3`; el pie "1 sola reserva Slurm..." reescrito para mencionar las 2 GPUs dedicadas (RAG + Tutor IA).
- Diapositiva 7: modelo de la tabla actualizado a 14B; se añadió una frase al callout "¿Por qué LanceDB + BM25?" mencionando que el Tutor IA usa un modelo de visión aparte en una segunda GPU, sin pasar por la recuperación.
- Diapositiva 8: cifras reales actualizadas (118→130 pruebas backend, 372→394 claves i18n, verificadas corriendo `pytest --collect-only` y un script de conteo sobre los 4 `.json` de locale antes de escribir el número).
- Validado con `scripts/office/validate.py` (XSD) — pasó limpio.

**`03-preguntas-demo.md`** (nuevo): preguntas de ejemplo probadas en vivo contra producción con el modelo de 14B, organizadas en 3 categorías (cita correcta, honestidad ante lo que la normativa no cubre, razonamiento sobre un caso ambiguo) más una lista de respaldo y un guion de demo de 4 minutos.
