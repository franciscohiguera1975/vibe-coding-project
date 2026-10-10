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
  - El algoritmo de recuperación (similitud de coseno, fuerza bruta en Python, `app.domain.services.rag_retrieval`) **no cambió**: sigue operando sobre lo que devuelve `list_all()` del repositorio, ahora respaldado por LanceDB en vez de Postgres. El cambio queda contenido a la capa de infraestructura (`LanceDbNormativaChunkRepository`, detrás del mismo `NormativaChunkRepository` Protocol) — nada en el dominio, los casos de uso, los routers, ni el frontend necesitó cambios.
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
