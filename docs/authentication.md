# Autenticación

JWT de acceso + refresco, firmados con `JWT_SECRET` (`HS256`).

## Flujo

1. `POST /api/auth/login` con `{email, password}` → `LoginUseCase` verifica el
   hash de contraseña (`BcryptPasswordHasher`, bcrypt directo — no `passlib`,
   ver [`troubleshooting.md`](troubleshooting.md)) y, si es válido, emite un
   access token y un refresh token (`JoseTokenService`, `python-jose`).
2. El frontend guarda ambos tokens (`LocalTokenStorage`, `localStorage`) y envía
   el access token en `Authorization: Bearer <token>` en cada petición
   (`ApiClient`).
3. Cuando una petición responde `401`, `ApiClient` intenta automáticamente
   `POST /api/auth/refresh` con el refresh token guardado; si el refresco
   funciona, reintenta la petición original una vez; si falla, limpia los
   tokens (el usuario queda deslogueado).

## Claims del token

Cada token incluye `sub` (id de usuario), `type` (`"access"` o `"refresh"`,
para que un refresh token no pueda usarse como access token), `jti` (UUID único,
para que dos tokens emitidos en el mismo segundo no sean idénticos), `iat` y
`exp`. `get_current_user` decodifica el token, valida `type == "access"`, y
**siempre vuelve a cargar el usuario desde la base de datos** (no confía en los
claims para autorizar — ver [`authorization.md`](authorization.md)); si el
usuario fue desactivado después de emitido el token, deja de autenticar.

## Vigencia

`JWT_ACCESS_EXPIRES_IN` / `JWT_REFRESH_EXPIRES_IN` (formato `Ns`/`Nm`/`Nh`/`Nd`,
ver `Settings.jwt_expires_seconds`), 15 minutos / 7 días por defecto.

## Contraseñas

`BcryptPasswordHasher` usa la librería `bcrypt` directamente (límite de 72 bytes
de bcrypt verificado explícitamente, con un `ValidationError` claro si se
excede, en vez de dejar que bcrypt falle con un error críptico).
