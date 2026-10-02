# Integración con Moodle

La plataforma expone una vista embebida de cada práctica, pensada para incrustarse
dentro de un curso de Moodle sin traer la navegación propia de la plataforma.

## Ruta de embebido

```
GET /practices/{slug}/embed
```

Esta ruta del frontend (no de la API) renderiza únicamente el contenido de la
práctica — título, objetivos, instrucciones, el ejecutor específico del tipo de
práctica (software o imagen) y el panel de resultado — sin encabezado, pie de
página ni menú de administración. Es la misma lógica que usa la página pública de
detalle de práctica (`/catalogo/{slug}`); solo cambia el layout que la envuelve.

Si el visitante no ha iniciado sesión, la vista embebida muestra un enlace de inicio
de sesión que, tras autenticarse, regresa a la misma URL de embebido.

## Uso en Moodle

En un curso de Moodle, agregue un recurso de tipo **URL** o **Página** con un
`<iframe>` apuntando a la URL pública de la práctica:

```html
<iframe
  src="https://<dominio-de-la-plataforma>/practices/software-01-simulacion-mru/embed"
  width="100%"
  height="900"
  style="border: 0;"
  title="Simulación de movimiento rectilíneo uniforme"
></iframe>
```

Recomendaciones:

- Use una altura generosa (800–1000px): el contenido crece según el tipo de
  práctica (los ejecutores de imagen con varias tarjetas de carga son más largos).
- El dominio de Moodle debe poder enmarcar el de la plataforma. En el despliegue
  con Docker/nginx (ver `docs/deployment.md`), configure la cabecera
  `Content-Security-Policy: frame-ancestors` con el dominio del Moodle institucional
  en lugar de bloquear el enmarcado con `X-Frame-Options: DENY`.
- Las cookies de sesión de la plataforma son independientes de las de Moodle: cada
  estudiante inicia sesión una vez dentro del iframe (no hay actualmente SSO/LTI).

## Autenticación desde el iframe

El `<iframe>` no comparte sesión con Moodle. La primera vez, el estudiante ve el
enlace "Inicie sesión" dentro del marco y se autentica con sus credenciales de la
plataforma; las siguientes cargas del mismo navegador reutilizan el token
almacenado localmente.

## API para integraciones más profundas

Para integraciones que no dependen de un iframe (por ejemplo, un bloque o plugin
de Moodle que consuma datos directamente), la API REST pública documentada en
`docs/api-reference.md` permite consultar el catálogo (`GET /api/practices`), el
detalle de una práctica (`GET /api/practices/{slug}`) e iniciar/enviar intentos
(`POST /api/practices/{slug}/start`, `POST /api/practices/attempts/{id}/submit`)
autenticando con JWT.

## Evolución futura (no implementada)

El Prompt Maestro contempla, como posible evolución, un **Web Component** o una
integración **LTI 1.3** para reemplazar el iframe simple por una experiencia
embebida nativa con paso de notas (grade passback) a Moodle. Se evaluó para esta
entrega y se decidió no implementarla: el iframe cubre el requisito de
"embebido en Moodle" sin la complejidad adicional de un consumer LTI (manejo de
claves, registro de la herramienta, paso de calificaciones), que queda fuera del
alcance académico de esta plataforma. Un web component expondría los mismos
ejecutores de práctica (`presentation/practices/registry.ts`) detrás de un
`customElement`, reutilizando la capa de aplicación tal cual.
