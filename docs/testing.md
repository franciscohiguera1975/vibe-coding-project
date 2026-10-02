# Testing

## Backend (`apps/backend/tests/`, pytest)

```bash
make test-backend   # 65 tests al momento de escribir esta guía
```

Organizado en tres capas, cada una verificando algo distinto:

- **`unit/`**: dominio puro y adaptadores sin estado externo —
  `test_image_counting.py` (la regla de conteo, casos conocidos de entrada/
  salida), `test_anthropic_adapter.py` (mapeo de la respuesta del SDK de
  Anthropic), `test_storage.py` (validación de archivos, path traversal).
- **`integration/`**: casos de uso completos contra una base de datos real
  (transacciones, repositorios, Unit of Work) — auth, prácticas, IA, el agente
  tutor, y el script de seed (`test_seed_script.py`, verifica que sea
  realmente idempotente).
- **`api/`**: la API HTTP completa vía `TestClient`, incluyendo RBAC
  (respuestas 401/403 correctas) y los endpoints de IA/agente/imágenes.

`AI_PROVIDER=mock` en el entorno de pruebas (nunca se consume un proveedor de IA
real ni se requiere `AI_API_KEY` para que la suite pase).

### ⚠️ `conftest.py` vacía la base de datos de desarrollo

Un fixture `autouse` (`_clean_database`) hace `TRUNCATE` de todas las tablas
antes de cada test, usando la misma `DATABASE_URL` del entorno — **no una base
de datos de pruebas separada**. Esto significa que correr `pytest` borra
cualquier dato sembrado manualmente. Siempre ejecutar `make seed` después de
`pytest` antes de volver a verificar algo manualmente en el navegador o con
`curl`. Ver [`troubleshooting.md`](troubleshooting.md).

## Frontend (`apps/frontend/src/`, Vitest + Testing Library)

```bash
make test-frontend   # 19 tests al momento de escribir esta guía
```

- `App.test.tsx`: routing de alto nivel (home, catálogo, 404, la vista de
  embebido sin la navegación pública).
- `registry.test.ts`: resolución tipo de práctica → componente, y el fallback
  para tipos desconocidos.
- `SoftwarePracticeRunner.test.tsx` / `ImagePracticeRunner.test.tsx`: lógica de
  cada ejecutor (detección del simulador, cálculo y envío, estrategias de
  evaluación de imagen).
- `ProtectedRoute.test.tsx`: las cuatro ramas del guard de RBAC (cargando,
  redirect a login, acceso restringido, contenido permitido).
- `api-client.test.ts`: el transform camelCase ↔ snake_case de `ApiClient`
  contra un `fetch` mockeado — incluye una regresión explícita del bug real de
  `OPAQUE_KEYS` (ver abajo).

Los servicios de infraestructura (`authService`, `practiceService`, …) se
mockean vía `vi.mock('@/infrastructure/container', ...)` para que los tests de
componentes/routing no dependan de un backend real.

## Una regresión real que motivó varios de estos tests

Durante el desarrollo, el transform recursivo camelCase/snake_case de
`ApiClient` corrompía silenciosamente el JSON libre de `content`/`evaluation`
(p. ej. `speed_kmh` → `speedKmh`), lo que rompía la detección
`'speed_kmh' in variables` del simulador y hacía caer el ejecutor al fallback
manual — sin ningún error visible, solo el componente equivocado renderizado.
Se encontró por verificación manual en el navegador (no por el type-checker ni
por un test previo), se corrigió con el conjunto `OPAQUE_KEYS`, y ahora tiene
cobertura directa en `api-client.test.ts` y `SoftwarePracticeRunner.test.tsx`
para que no pueda reaparecer en silencio.
