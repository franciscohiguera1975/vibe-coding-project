# Modelo de prácticas

Una práctica es una entidad configurable, no código específico por práctica: el
mismo modelo sirve para cualquier práctica futura de un tipo ya registrado, sin
tocar el núcleo de la plataforma (Prompt Maestro §16/§34).

## Campos

| Campo | Descripción |
|---|---|
| `slug`, `title`, `description` | identificación y presentación |
| `type` | determina qué ejecutor de la UI se usa (ver `architecture.md` §Registro de tipos) |
| `category_slug`, `technologies`, `tags`, `difficulty`, `estimated_time_minutes` | metadatos de catálogo/filtrado |
| `objectives`, `instructions` | contenido pedagógico mostrado al estudiante |
| `content` | JSON libre específico del tipo de práctica (modelo físico, regla de conteo, ejemplos…) |
| `evaluation` | estrategia de evaluación + parámetros (ver [`ai.md`](ai.md) §Evaluación) |
| `ai_configuration` | configuración de pistas/IA para esa práctica |
| `embedding_configuration` | si la práctica es embebible y su layout (ver [`moodle-integration.md`](moodle-integration.md)) |
| `metadata` | notas internas (p. ej. `extends` para prácticas que parten de otra) |
| `status` | `draft` / `published` / `archived` |

`content`/`evaluation`/`ai_configuration`/`embedding_configuration`/`metadata`
viajan como JSON opaco entre el backend y el frontend — ver la nota sobre
`OPAQUE_KEYS` en `architecture.md`.

## Agregar un tipo de práctica nuevo

1. Backend: el `content`/`evaluation` de ese tipo no necesita un schema
   especial — es JSON libre; si la evaluación necesita una estrategia nueva,
   agregarla a `RuleBasedEvaluationAdapter`.
2. Frontend: crear un componente que implemente `PracticeRunnerProps` y
   agregarlo a `REGISTRY` en `presentation/practices/registry.ts`. Ninguna otra
   parte del flujo de ejecución de prácticas necesita cambiar.

Agregar una práctica nueva de un tipo **ya existente** no requiere ningún cambio
de código — solo una fila nueva (vía seed o el panel de administración).

## Las 4 prácticas iniciales (`database/seeds/practices_data.py`)

Dos tipos, cada uno con una práctica de construcción y una de extensión sobre la
misma base (no se sustituyó contenido pedagógico por ejemplos genéricos —
Prompt Maestro §37):

- **`software-01-simulacion-mru`**: construir, paso a paso y con asistencia de
  IA, una actividad interactiva de predicción/verificación para un modelo físico
  simple (MRU: distancia = velocidad × tiempo), con la secuencia fija predecir →
  ajustar → ejecutar → observar → explicar, controles accesibles por teclado, y
  verificación contra ejemplos numéricos conocidos.
- **`software-02-depuracion-mru`**: depurar una versión con tres errores
  intencionales de esa misma simulación (validación de límites, caso borde con
  tiempo cero, accesibilidad de teclado), verificando cada corrección contra los
  criterios de aceptación de la práctica base — ejercicio de análisis y
  evaluación de código generado por IA, no de construcción desde cero.
- **`image-01-conteo-circulos`**: construir un prototipo que cuenta círculos de
  papel de colores en imágenes con una regla de conteo explícita (qué cuenta,
  qué no, cuándo la imagen es ilegible, qué se conserva siempre), comparando el
  conteo propuesto contra una referencia humana sobre un conjunto de desarrollo
  y uno reservado para prueba.
- **`image-02-diagnostico-errores`**: a partir de los resultados de
  `image-01` sobre el conjunto reservado, clasificar los errores por condición
  (iluminación, superposición, desenfoque) y proponer un ajuste a la regla de
  conteo — ejercicio de interpretación y mejora de método, no de construcción de
  una herramienta nueva.

Los ejercicios en sí (objetivos, instrucciones, criterios) no citan ninguna
fuente externa por nombre — presentan el paso a paso de forma autocontenida.
