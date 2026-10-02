# AI Tutor Agent

`POST /api/agent/run` (`AITutorAgent`, `application/services/agent/`).

## Decisión de diseño: orquestador determinista, no un planificador LLM libre

El agente es código Python que decide qué herramientas invocar según los
parámetros explícitos de la petición (`submission_id`, `trial_answer`,
`image_base64`, …) — **el modelo de lenguaje no decide el plan de ejecución**,
solo sintetiza la respuesta final a partir del contexto ya reunido por las
herramientas. Se evaluó y se descartó deliberadamente un loop tipo ReAct/
framework de agentes (LangChain u otro) a favor de este enfoque, priorizando lo
que el Prompt Maestro §11 pide explícitamente — "objetivo, contexto,
herramientas permitidas, límites de iteraciones/tokens, control de permisos,
trazabilidad, manejo de errores y protección contra ciclos infinitos" — sobre
autonomía abierta. Un beneficio práctico adicional: es completamente testeable
sin mocks de un LLM real para la parte de decisión (solo la síntesis final llama
al `AIProvider`).

El agente **no ejecuta ninguna acción administrativa o destructiva** — las 7
herramientas son todas de lectura o generación.

## Herramientas (`application/services/agent/tools.py`)

| Herramienta | Qué hace |
|---|---|
| `get_practice` | lee una práctica por slug |
| `get_student_progress` | lee el progreso del estudiante en esa práctica |
| `analyze_submission` | lee una submission ya registrada |
| `generate_hint` | pide una pista al `AIProvider` |
| `validate_answer` | valida una respuesta de prueba contra `EvaluationPort` |
| `analyze_image` | analiza una imagen con el `AIProvider` |
| `generate_feedback` | genera retroalimentación sobre una submission evaluada |

`TOOL_REGISTRY` las mapea por nombre; `TOOL_ALLOWLIST` (derivada del mismo
registro) es la lista blanca que `call_tool` verifica en cada invocación — un
nombre fuera de la lista se registra como `DENIED` y aborta la sesión con
`PermissionDeniedError`.

## Límites y protección contra ciclos infinitos

- `max_iterations` (`AI_AGENT_MAX_ITERATIONS`, 8 por defecto): cada llamada a
  herramienta (y la síntesis final) incrementa un contador; al excederlo, la
  llamada se registra como `DENIED` con el motivo "límite de iteraciones
  excedido", la sesión se marca `ERROR`, y se lanza `AgentLimitExceededError`
  (mapeado a HTTP 429 — ver [`api.md`](api.md)).
- `max_tokens` (`AI_AGENT_MAX_TOKENS`, 4000 por defecto): presupuesto aproximado
  (conteo de palabras, no un tokenizador real — solo para comparar consumo
  relativo entre sesiones) que acota el `max_tokens` de la llamada final de
  síntesis (`remaining_budget = max(200, max_tokens - tokens_used)`).
- El flujo de herramientas que se invocan por petición está fijo en código
  (`get_practice` y `get_student_progress` siempre; `analyze_submission` +
  `generate_feedback` solo si hay `submission_id`; `validate_answer` solo si hay
  `trial_answer`; `analyze_image` solo si hay `image_base64` y la práctica es de
  tipo imagen; `generate_hint` como fallback si no hay ninguno de los
  anteriores) — no hay recursión ni un loop que pueda reinvocarse a sí mismo.

## Trazabilidad

Cada ejecución crea una fila en `ai_sessions` (estado, iteraciones usadas,
tokens usados, práctica asociada); cada mensaje usuario/asistente se guarda en
`ai_messages`; **cada llamada a herramienta** (exitosa, denegada o con error) se
guarda en `ai_tool_calls` con sus argumentos y resultado — incluyendo los casos
denegados por el límite de iteraciones o por una herramienta fuera de la lista
blanca. Esto permite auditar exactamente qué hizo el agente en cada sesión.

## Control de permisos y manejo de errores

El agente recibe el `actor` (usuario autenticado) y lo pasa a cada herramienta,
que a su vez reutiliza los mismos casos de uso y repositorios que el resto de la
plataforma (sujetos a las mismas reglas de dominio). Un `DomainError` levantado
por una herramienta se captura, se registra como `ERROR` en `ai_tool_calls`,
finaliza la sesión como `ERROR`, y se re-propaga (no se traga el error ni se
reintenta silenciosamente).
