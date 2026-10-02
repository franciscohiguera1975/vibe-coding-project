# Solución de problemas

## El seed se ejecutó pero no veo datos / "Práctica no encontrada" en el navegador

`pytest` vacía la base de datos de desarrollo en cada corrida (ver
[`testing.md`](testing.md)). Ejecute `make seed` de nuevo después de correr la
suite de pruebas y antes de volver a probar manualmente.

## `could not connect to server` / puerto 5432 ocupado

Un PostgreSQL nativo del host suele ocupar el puerto 5432. `docker-compose.yml`
mapea el servicio `postgres` al puerto **5433** del host por defecto
(`POSTGRES_PORT`), y `DATABASE_URL` en `.env.example` ya apunta ahí. Si cambió
`POSTGRES_PORT`, actualice `DATABASE_URL` a juego.

## Falla la instalación de Pillow/numpy en Python muy nuevo

Versiones muy nuevas de Python pueden no tener wheels precompilados para
versiones antiguas de Pillow (incompatibilidad con la API de libwebp del
sistema). El proyecto fija `Pillow>=11.0,<13` y `numpy>=2.1,<3` en
`pyproject.toml`, que sí tienen wheels para Python recientes — si aun así falla,
compruebe que no haya un pin más antiguo en un entorno virtual preexistente.

## `email-validator` rechaza un correo `.local` o `.test`

`.local` y `.test` son TLDs reservados (RFC 2606/6762) y `pydantic[email]` los
rechaza por diseño. Use un dominio como `.dev` para correos de prueba/seed
(p. ej. `admin@vibecoding-platform.dev`).

## El admin del seed en Docker quedó con credenciales vacías

Si `docker-compose.yml` llegara a fijar `SEED_ADMIN_EMAIL`/`SEED_ADMIN_PASSWORD`
con un valor por defecto vacío (`${VAR:-}`), eso pisa el valor por defecto del
script con una cadena vacía real — distinto de no definir la variable en
absoluto. El compose actual evita esto a propósito (ver
[`docker.md`](docker.md) §Nota sobre `SEED_ADMIN_EMAIL`); si encuentra un
usuario con `email=''` en la base, es seguro borrarlo
(`DELETE FROM users WHERE email = '';`) y volver a correr el seed.

## Una práctica de tipo software no muestra el simulador

Si `content.model.variables` no contiene exactamente `speed_kmh`/`time_h`
(claves en snake_case), `SoftwarePracticeRunner` cae al formulario de
autoevaluación manual sin ningún error. Esto puede pasar si un cliente HTTP
transforma las claves de `content` a camelCase — `content`/`evaluation`/
`metadata`/etc. deben viajar como JSON opaco, sin transformar sus claves
internas (ver `OPAQUE_KEYS` en `architecture.md` y la regresión documentada en
[`testing.md`](testing.md)).

## `ValueError: password cannot be longer than 72 bytes`

Límite real de bcrypt. `BcryptPasswordHasher` lo valida explícitamente antes de
hashear y levanta un `ValidationError` de dominio (HTTP 422) en vez de dejar que
bcrypt falle con un error de bajo nivel.

## CORS bloquea las peticiones del frontend

`CORS_ALLOWED_ORIGINS` debe incluir exactamente el origen desde el que sirve el
frontend (protocolo + host + puerto). En despliegue nativo con nginx
reenviando `/api` bajo el mismo origen que el frontend, CORS no debería ni
activarse — ver [`native-deployment.md`](native-deployment.md).
