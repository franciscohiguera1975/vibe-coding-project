# IA desacoplada

El dominio y los casos de uso solo conocen el puerto `AIProvider`
(`application/ports/ai_provider.py`):

```python
class AIProvider(Protocol):
    def generate_text(self, prompt: str, *, system: str | None = None, max_tokens: int = 1000) -> str: ...
    def analyze_image(self, image_bytes: bytes, *, instructions: str, content_type: str) -> ImageAnalysisResult: ...
    def generate_feedback(self, *, context: dict[str, Any]) -> str: ...
```

Qué adaptador se usa se decide por `AI_PROVIDER` (ver
[`configuration.md`](configuration.md)):

- **`mock`** (`MockAIAdapter`, valor por defecto en desarrollo y siempre en
  pruebas): no hace llamadas de red, genera texto determinista a partir del
  contexto recibido y aplica la regla de conteo de imágenes real localmente
  (ver más abajo). Permite ejercitar el flujo completo (pistas, feedback,
  análisis de imagen, agente) sin depender de credenciales externas.
- **`anthropic`** (`AnthropicAdapter`): llama a la API de Claude
  (`AI_API_KEY`, `AI_MODEL`) para `generate_text`/`generate_feedback`, y usa
  visión real del modelo para `analyze_image`.

## Casos de uso que consumen el puerto

- `GenerateAIHint` (`POST /api/ai/hint`): pista contextual para una práctica.
- `GeneratePracticeFeedback` (`POST /api/ai/feedback`): retroalimentación sobre
  una submission ya evaluada.
- `AnalyzeImage` (`POST /api/images/analyze`, ver más abajo).
- El AI Tutor Agent (ver [`ai-agents.md`](ai-agents.md)) también usa el puerto,
  pero a través de sus propias herramientas controladas, no directamente.

## Manejo de imágenes

`StoragePort` (`upload`/`delete`/`get_url`) desacopla dónde viven los archivos
subidos de la lógica de negocio:

- `LocalStorageAdapter` (por defecto, `STORAGE_PROVIDER=local`): guarda en disco
  bajo `STORAGE_LOCAL_PATH`, con claves `uuid4().hex` (no expone el nombre
  original) y protección explícita contra path traversal.
  `ProcessImage`/`images.py` validan MIME, extensión y tamaño
  (`STORAGE_MAX_UPLOAD_MB`) antes de guardar.
- `MinIOAdapter` / `S3Adapter` (`STORAGE_PROVIDER=minio|s3`): stubs con la
  interfaz completa de `StoragePort`, documentados como no operativos sin
  credenciales — suficientes para dejar el punto de extensión listo sin añadir
  una dependencia de infraestructura real a un entregable educativo.

### Regla de conteo de objetos

`infrastructure/ai/image_counting.py` implementa una regla explícita y
determinista (sin modelo entrenado): redimensiona la imagen, calcula una máscara
de saturación de color (`max(R,G,B) - min(R,G,B) > 40`, separa objetos de color
de un fondo neutro), etiqueta componentes conexas con una pila explícita (sin
`scipy`) y descarta regiones demasiado pequeñas para ser ruido. `MockAIAdapter`
la usa directamente para `analyze_image`; `AnthropicAdapter` resuelve el mismo
problema con visión real del modelo cuando `AI_PROVIDER=anthropic`. Una imagen
no decodificable se reporta como `warnings=["imagen ilegible: ..."]` en vez de
fallar la petición.

## Evaluación de prácticas

`RuleBasedEvaluationAdapter` (`EvaluationPort`) soporta tres estrategias,
elegidas por `practice.evaluation.strategy`:

- `numeric_match`: compara campos numéricos del envío contra valores esperados
  con tolerancia.
- `count_comparison`: compara conteos propuestos contra una referencia humana
  por imagen, con un umbral de puntaje mínimo.
- `manual`: no evalúa automáticamente; queda marcada para revisión de un
  docente (ver el flujo en la UI del ejecutor de prácticas de imagen).
