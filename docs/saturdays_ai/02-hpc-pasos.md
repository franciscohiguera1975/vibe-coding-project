# Pasos a ejecutar en el HPC de CEDIA

Runbook para que el usuario ejecute en su propia sesión del HPC (`hpc.cedia.edu.ec`) — Claude Code no tiene acceso a ese servidor, así que estos pasos los corre la persona. Reescrito completo el 2026-10-09 tras descubrir que la cuenta tiene un límite de **1 sola reserva de Slurm activa a la vez** (`QOSMaxJobsPerUserLimit`) — el diseño anterior de "dos reservas independientes" no es viable aquí. Esta es la versión definitiva.

**Qué se arma**: **3 servicios** dentro de **una sola reserva de Slurm con 2 GPUs** (actualizado 2026-10-11 — antes eran 2 servicios con 1 GPU; ver `00-plan.md` para el porqué del cambio — en corto, el tutor de la plataforma se conecta ahora al mismo tipo de cómputo real que ya usaba el RAG):

| Servicio | Modelo | GPU | Puerto local | Para qué |
|---|---|---|---|---|
| **vLLM (texto)** | `Qwen/Qwen2.5-7B-Instruct` | GPU 0 | `8001` | Genera las respuestas del RAG (validación de sílabos, evaluación) — ya validado, 15/15 |
| **TEI** | `intfloat/multilingual-e5-large` | (CPU; toca GPU 0 levemente) | `8002` | Calcula los embeddings de consulta y corpus |
| **vLLM (visión)** | `Qwen/Qwen2.5-VL-7B-Instruct` | GPU 1 | `8003` | Sirve al AI Tutor (pistas de texto Y análisis de imágenes) — **nuevo** |

Los 3 corren dentro de la misma reserva de Slurm (ahora con `--gres=...:2` en vez de `:1`), cada uno conectado al nodo por `ssh` directo salvo el primero, sin volver a pasar por `salloc`/`srun` (eso es lo que evita el límite de 1 job). Cada uno se tunela por separado hacia el VPS. No es un servicio permanente: se levanta antes de usar RAG/tutor (prueba o demo) y se apaga después (ver `00-plan.md` §5 para el porqué).

**Dos formas equivalentes de hacer esto — elige una:**
- **Opción A (abajo, secciones 0-5): 6 pestañas** (3 servicios + 3 túneles), cada una en primer plano — más fácil de ver el progreso de cada servicio en vivo, cada pieza aislada en su propia ventana.
- **Opción B (sección 10, al final): 1 sola pestaña**, con los 6 procesos en segundo plano (`nohup` + `disown`) — mismo resultado, menos ventanas que gestionar, y de hecho más resistente a un cierre accidental de la pestaña (los procesos sobreviven aunque la cierres, mientras la reserva de Slurm siga activa). **Recomendada ahora que son 3 servicios en vez de 2** — 6 pestañas es mucho para gestionar a mano.

**6 pestañas de terminal en total (Opción A), ninguna se cierra mientras dure la sesión:**

| Pestaña | Qué hace |
|---|---|
| 1 | La única reserva (`salloc`, ahora con 2 GPUs) + arranca **vLLM texto** (GPU 0) |
| 2 | `ssh` directo al mismo nodo + arranca **TEI** |
| 3 | `ssh` directo al mismo nodo + arranca **vLLM visión** (GPU 1) |
| 4 | `ssh` directo al mismo nodo + túnel de vLLM texto (8001→8765) |
| 5 | `ssh` directo al mismo nodo + túnel de TEI (8002→8766) |
| 6 | `ssh` directo al mismo nodo + túnel de vLLM visión (8003→8767) |

Por qué funciona conectarse por `ssh` directo en vez de `srun --jobid=...` una segunda vez: `srun` pide un nuevo "paso" (step) dentro del job, y eso compite por el único cupo de tarea que dio `salloc -n 1` (se cuelga o falla). Una conexión `ssh` directa al nodo no pasa por esa cola de Slurm — simplemente aprovecha que, mientras el job 1 siga activo, el clúster te deja entrar a ese nodo por SSH normal.

---

## 0. Preparación compartida — SOLO LA PRIMERA VEZ

```bash
ssh francisco.higuera__ute.edu.ec@hpc.cedia.edu.ec
```

Si no conecta por SSH, usar el acceso web en `https://hpc.cedia.edu.ec` → "NVIDIA DeepOps Desktop" (sección 2 del `Manual HPC Completo.pdf`).

**Llave SSH para los túneles** (sirve desde el nodo de login, no hace falta reserva):

```bash
ssh-keygen -t ed25519 -f ~/.ssh/hpc_tunnel_key -N ""
cat ~/.ssh/hpc_tunnel_key.pub
```

Copia esa línea completa y pásasela a Claude Code — la autoriza en el VPS (`authorized_keys` del usuario `deploy`). Se hace una sola vez; la llave queda guardada en tu `$HOME` para siempre.

---

## 1. Pestaña 1 — la única reserva, y vLLM

**Si ya tienes una reserva activa de antes (1 sola GPU), libérala primero** — no se le puede agregar una segunda GPU a una reserva ya concedida, hay que pedirla de nuevo:
```bash
scancel <JOBID_VIEJO>
```

Antes de reservar, revisa qué nodo está menos cargado (otros usuarios pueden estar saturando uno de los dos — ver §9 para más detalle):
```bash
sinfo -N -o "%N %C %O" -p gpu
```

```bash
ssh francisco.higuera__ute.edu.ec@hpc.cedia.edu.ec
salloc -p gpu -n 1 -c 20 --mem=48G --gres=gpu:a100-sxm4-40gb:2 --time=04:00:00
```

(`-c 20 --mem=48G`: casi el doble que antes, porque esta misma reserva ahora corre **3 procesos** — dos vLLM y un TEI — en vez de dos. `:2` en `--gres` pide las 2 GPUs completas, una para cada vLLM; TEI toca la GPU 0 levemente pero no necesita una propia. Si quieres fijar un nodo en particular tras revisar `sinfo`, agrega `--nodelist=compute-0-X`.)

**Nota (descubierto 2026-10-09)**: los tipos MIG del Anexo 1 del manual (`a100_1g.5gb`, `a100_2g.10gb`, `a100_3g.20gb`) no están configurados en los nodos de `gpu-dev`/`gpu` — ahí solo existe el GPU completo `a100-sxm4-40gb`. Por eso se pide ese tipo exacto.

**Nota (descubierto 2026-10-11, importante)**: la partición **`gpu-dev`** (la que usa todo este documento desde el inicio del proyecto) tiene un límite de QOS de **máximo 1 GPU por job** (`QOSMaxGRESPerJob`) — pedir `:2` ahí falla siempre, sin importar cuánta CPU/memoria pidas. La partición **`gpu`** (mismos nodos físicos, `compute-0-[1-2]`, solo que con otra QOS) sí permite hasta 2 GPUs por job, con más margen de CPU (`cpu=160` vs `cpu=16`) — por eso el comando de arriba usa `-p gpu`, no `-p gpu-dev`. Si en algún momento vuelves a necesitar solo 1 GPU (el diseño original de 2 servicios), `gpu-dev` sigue siendo válido y es la partición "de siempre" para ese caso.

La salida muestra el `JOBID` y el nodo asignado — **anótalos, los necesitas para las otras 5 pestañas**:

```
salloc: Granted job allocation 29124      <- JOBID
salloc: Nodes compute-0-1 are ready for job  <- NODO
```

Si los pierdes de vista: `squeue -u francisco.higuera__ute.edu.ec` (columnas `JOBID` y `NODELIST`).

Entrar al nodo:

```bash
srun --jobid=JOBID --pty bash
```

El prompt cambia de `...@login1` a `...@NODO` — recién ahí existen herramientas como `enroot`.

### 1.1. Primera vez únicamente: crear el contenedor de vLLM

```bash
enroot import docker://vllm/vllm-openai:latest
enroot create --name vllm-server vllm+vllm-openai+latest.sqsh
```

Si dice `[ERROR] File already exists`, no es un error — ya se hizo antes, seguir directo a 1.2.

### 1.2. Arrancar vLLM (texto)

```bash
CUDA_VISIBLE_DEVICES=0 enroot start --mount $HOME --root --rw vllm-server \
  Qwen/Qwen2.5-7B-Instruct \
  --port 8001 \
  --max-model-len 4096
```

**Importante**: la imagen `vllm/vllm-openai` tiene su `ENTRYPOINT` fijo en `vllm serve` — lo que le pases a `enroot start <contenedor> <comando>` se agrega como argumento a ese entrypoint, no lo reemplaza. No escribas `vllm serve ...` ni `python3 -m vllm.entrypoints...` delante del modelo (ambos rompen el comando) — el modelo y las opciones van directo, como arriba.

**`CUDA_VISIBLE_DEVICES=0` es nuevo (2026-10-11)**: con 2 GPUs en la misma reserva, si no fijas cuál usa cada proceso, los dos vLLM intentarían tomar la GPU 0 por defecto y chocarían. Este queda en la GPU 0; el de visión (sección 2.5) va en la GPU 1.

Esperar a `INFO: Application startup complete.` — no devuelve el prompt, se queda corriendo ahí (correcto, no es que se colgó). El modelo (`Qwen/Qwen2.5-7B-Instruct`, abierto, sin token de Hugging Face) se descarga solo la primera vez y queda cacheado en `$HOME/.cache/huggingface`. **No cerrar esta pestaña.**

---

## 2. Pestaña 2 — conectarse al mismo nodo, y TEI

Pestaña nueva, **sin `salloc` ni `srun`** — directo por SSH al nodo de la Pestaña 1:

```bash
ssh francisco.higuera__ute.edu.ec@hpc.cedia.edu.ec
ssh NODO
```

(ej. `ssh compute-0-1` — usa el nodo real que anotaste en la sección 1).

### 2.1. Primera vez únicamente: crear el contenedor de TEI

```bash
enroot import docker://ghcr.io#huggingface/text-embeddings-inference:1.5
enroot create --name tei-server huggingface+text-embeddings-inference+1.5.sqsh
```

Notas:
- El registro de una imagen que no está en Docker Hub va **separado con `#`**: `docker://ghcr.io#huggingface/...`, nunca `docker://ghcr.io/huggingface/...` (eso último falla con `401 Unauthorized`).
- El nombre del `.sqsh` generado no incluye el registro, solo la ruta de la imagen — de ahí `huggingface+text-embeddings-inference+1.5.sqsh`. Si no coincide, `ls *.sqsh` después del `import` confirma el nombre real.
- Si dice `[ERROR] File already exists`, no es un error — ya se hizo antes, seguir directo a 2.2.

### 2.2. Arrancar TEI

**Importante (descubierto 2026-10-09)**: igual que vLLM, la imagen de TEI tiene su binario (`text-embeddings-router`) fijo como `ENTRYPOINT` — no lo repitas en el comando, o se interpreta como un argumento inesperado (`error: unexpected argument 'text-embeddings-router' found`). Pasa solo las opciones:

```bash
enroot start --mount $HOME --root --rw --env HF_ENDPOINT=https://huggingface.co tei-server \
  --model-id intfloat/multilingual-e5-large \
  --port 8002
```

(el `--env HF_ENDPOINT=...` es necesario — sin él, TEI falla al descargar el modelo con `relative URL without a base`, porque esa variable viene vacía/mal configurada dentro del contenedor por defecto).

**TEI corre en CPU, no necesita GPU** — el modelo (560M parámetros) responde rápido para una consulta a la vez, que es nuestro caso de uso; la GPU de la reserva la usa solo vLLM. No devuelve el prompt — se queda corriendo (correcto). **No cerrar esta pestaña.**

---

## 3. Pestaña 3 (nueva, 2026-10-11) — vLLM con visión, para el tutor

Pestaña nueva, conectando otra vez al mismo nodo (igual que la Pestaña 2):

```bash
ssh francisco.higuera__ute.edu.ec@hpc.cedia.edu.ec
ssh NODO
```

### 3.1. Primera vez únicamente: crear el contenedor

Reusa la misma imagen `vllm/vllm-openai` ya descargada para el modelo de texto — no hace falta volver a importarla, solo crear un contenedor con otro nombre:

```bash
enroot create --name vllm-vl-server vllm+vllm-openai+latest.sqsh
```

Si dice `[ERROR] File already exists`, no es un error — seguir directo a 3.2.

### 3.2. Arrancar vLLM (visión)

```bash
CUDA_VISIBLE_DEVICES=1 enroot start --mount $HOME --root --rw vllm-vl-server \
  Qwen/Qwen2.5-VL-7B-Instruct \
  --port 8003 \
  --max-model-len 8192 \
  --trust-remote-code
```

Notas:
- `CUDA_VISIBLE_DEVICES=1`: lo pone en la segunda GPU de la reserva, separado del modelo de texto (que usa la GPU 0, sección 1.2) — sin esto, los dos vLLM pelean por la misma GPU.
- `--max-model-len 8192` (el doble que el modelo de texto): los modelos con visión consumen más tokens de contexto por imagen (la codificación de la imagen ocupa cientos o miles de tokens, según su resolución) — si ves un error de contexto insuficiente, es la primera variable a subir.
- `--trust-remote-code`: Qwen2.5-VL trae código propio (no solo pesos) que `vllm` necesita poder ejecutar para cargar el modelo correctamente.
- **Primera vez que este proyecto sirve un modelo con visión por vLLM** — a diferencia del modelo de texto (ya probado varias veces), es razonable que aparezca algún error nuevo la primera vez; avisa a Claude Code con el mensaje exacto si pasa, para diagnosticarlo igual que los errores anteriores de este documento.

No devuelve el prompt — se queda corriendo (correcto, esperar a `INFO: Application startup complete.`). **No cerrar esta pestaña.**

---

## 4. Pestaña 4 — túnel de vLLM (texto)

Pestaña nueva, conectando otra vez al mismo nodo:

```bash
ssh francisco.higuera__ute.edu.ec@hpc.cedia.edu.ec
ssh NODO
curl http://localhost:8001/v1/models
```

Si responde con JSON del modelo, abrir el túnel:

```bash
ssh -i ~/.ssh/hpc_tunnel_key -N -R 8765:localhost:8001 deploy@74.208.222.22
```

(si pregunta por confirmar el host la primera vez, aceptar). **No cerrar esta pestaña.**

## 5. Pestaña 5 — túnel de TEI

Pestaña nueva, conectando otra vez al mismo nodo:

```bash
ssh francisco.higuera__ute.edu.ec@hpc.cedia.edu.ec
ssh NODO
curl http://localhost:8002/health
curl -s -o /dev/null -w "HTTP %{http_code}\n" http://localhost:8002/health
```

Abrir el túnel:

```bash
ssh -i ~/.ssh/hpc_tunnel_key -N -R 8766:localhost:8002 deploy@74.208.222.22
```

**No cerrar esta pestaña.**

## 6. Pestaña 6 — túnel de vLLM (visión)

Pestaña nueva, conectando otra vez al mismo nodo:

```bash
ssh francisco.higuera__ute.edu.ec@hpc.cedia.edu.ec
ssh NODO
curl http://localhost:8003/v1/models
```

Abrir el túnel:

```bash
ssh -i ~/.ssh/hpc_tunnel_key -N -R 8767:localhost:8003 deploy@74.208.222.22
```

**No cerrar esta pestaña.** Los 3 túneles (4, 5 y 6) apuntan al mismo VPS con puertos remotos distintos (8765, 8766 y 8767) — no chocan entre sí aunque los tres salgan del mismo nodo.

---

## 7. Verificación y carga de datos (esto lo hace Claude Code, no tú)

Una vez las 6 pestañas están arriba:

1. Confirmar desde el VPS que los 3 puertos tunelados responden (`curl http://localhost:8765/v1/models`, `curl http://localhost:8766/health`, `curl http://localhost:8767/v1/models`).
2. `RAG_BASE_URL`/`EMBEDDING_BASE_URL` (RAG) ya están configurados de antes — no cambian. Nuevo: `AI_PROVIDER=openai_compatible`, `AI_BASE_URL=http://localhost:8767/v1`, `AI_MODEL=Qwen/Qwen2.5-VL-7B-Instruct`, `AI_VISION_BASE_URL=http://localhost:8767/v1`, `AI_VISION_MODEL=Qwen/Qwen2.5-VL-7B-Instruct` en el `.env` de producción (el tutor usa el mismo modelo de visión para texto e imagen, ver `00-plan.md`).
3. Cargar los embeddings del corpus (solo hace falta la primera vez que el túnel queda arriba; es idempotente):
   ```bash
   cd /opt/vibe-coding-platform/apps/backend
   .venv/bin/python scripts/rag/load_chunks.py
   ```
   Guarda los vectores en **LanceDB**, embebido en el propio VPS (no en Postgres ni en el HPC — ver `00-plan.md` §5).
4. Probar las pantallas "Validación de sílabos" y "Evaluación", y pedirle una pista al tutor IA, en la plataforma.

## Al terminar

En cada una de las 6 pestañas, `Ctrl+C` (para los túneles) o simplemente cerrar. Luego, en la Pestaña 1 (o desde cualquiera con `squeue -u francisco.higuera__ute.edu.ec`), liberar la única reserva:

```bash
scancel JOBID
```

Anota aquí la fecha y duración real de la sesión, para la diapositiva de "arquitectura y costos".

---

## 8. Si algo falla

- **`enroot start ... vllm-vl-server` da `[ERROR] No such file or directory: .../enroot/vllm-vl-server`** (descubierto 2026-10-11): te saltaste el paso de creación (sección 3.1) — `enroot start` no crea el contenedor, solo lo arranca si ya existe. No es un problema del nodo (`$HOME` es almacenamiento compartido NFS, visible desde cualquier nodo) — corre primero `enroot create --name vllm-vl-server vllm+vllm-openai+latest.sqsh` (reutiliza la imagen ya descargada, no baja nada nuevo) y luego reintenta el arranque.
- **Un `enroot start` de vLLM da `ModuleNotFoundError: No module named 'vllm'` (no el error de "modelo no válido")**: el contenedor quedó corrupto. Reconstruir desde cero (cambiar `vllm-server` por `vllm-vl-server` si es el de visión el que falló):
  ```bash
  enroot remove vllm-server
  rm vllm+vllm-openai+latest.sqsh
  enroot import docker://vllm/vllm-openai:latest
  enroot create --name vllm-server vllm+vllm-openai+latest.sqsh
  ```
- **El túnel no conecta**: revisar que la llave pública sigue en `/home/deploy/.ssh/authorized_keys` del VPS.
- **vLLM no carga el modelo a tiempo**: hay respaldo — `RAG_LLM_PROVIDER` puede apuntar a GitHub Models (capa gratuita) cambiando una sola variable de entorno, sin tocar código. Vale la pena probarlo una vez antes del día de la demo.
- **La GPU pedida (`a100-sxm4-40gb`) no está disponible**: revisar `sinfo -p gpu`; si está ocupado, la partición `interactive` con `a100_2g.10gb` es la alternativa más chica (pero no permite 2 GPUs completas — solo sirve para volver al diseño de 1 GPU).
- **Un `salloc`/`srun` nuevo se queda en `PD` con razón `(QOSMaxJobsPerUserLimit)`**: tu cuenta solo permite **1 reserva activa a la vez** — no es falta de recursos del clúster, es un tope de tu cuenta. Por eso todo este documento usa una sola reserva compartida para los 3 servicios (secciones 1-6) en vez de varias independientes. No intentar una segunda reserva mientras la primera siga activa.
- **Un `srun --jobid=...` se queda colgado o da `Job/step already completing or completed`**: estás tratando de crear un segundo "paso" en la misma reserva (`-n 1` solo da un cupo). Para cualquier conexión adicional al mismo nodo, usar `ssh <nodo>` directo, nunca `srun` otra vez.
- **Viste un `JOBID` de otro usuario con tu mismo nombre en `squeue`**: la columna `USER` se corta a 8 caracteres — puede coincidir con la de alguien más (pasó con `francisco.mendoza__yachaytech.edu.ec`, truncado igual que `francisco.higuera__ute.edu.ec`). Antes de cancelar un job que no reconoces, confirmar con `scontrol show job <JOBID>` (revisar el campo `Command`/`WorkDir`, ahí se ve el usuario real) — nunca cancelar un job que no sea tuyo.
- **Cerraste por error la pestaña de la Pestaña 1 (el `salloc`)**: la reserva murió, y con ella todo lo que corría adentro (los 3 servicios). No hay que recuperarla — repetir desde la sección 1 (los contenedores y modelos siguen descargados, así que es rápido).
- **Los dos vLLM intentan usar la misma GPU / uno falla con un error de memoria al arrancar el segundo**: falta el `CUDA_VISIBLE_DEVICES` (0 para el de texto, 1 para el de visión, secciones 1.2 y 3.2) — revisa que cada `enroot start` lo tenga.
- **El modelo de visión da un error de "contexto insuficiente" (context length exceeded) al analizar una imagen**: sube `--max-model-len` en la sección 3.2 (empezar en 8192, subir a 16384 si persiste) — las imágenes consumen más tokens de contexto que el texto solo.
- **`salloc: error: QOSMaxGRESPerJob`** al pedir `--gres=gpu:a100-sxm4-40gb:2`: estás en la partición equivocada — `gpu-dev` no permite más de 1 GPU por job. Usa `-p gpu` en vez de `-p gpu-dev` (ver la nota de la sección 1 y el diagnóstico de §9 para confirmar el límite exacto de cada partición).
- **`salloc: error: QOSMaxCpuPerUserLimit`** al pedir `-c 20` (o más): esa partición tiene un tope de CPU por job más bajo de lo que pediste (p. ej. `gpu-dev` tope en `cpu=16`) — baja el `-c` o cambia de partición (`-p gpu` admite hasta `cpu=160`). Confirmar el tope exacto con el comando de `sacctmgr` en §9.

## 9. Comandos de diagnóstico (de consulta, no reservan ni cambian nada)

```bash
sacctmgr show qos format=Name,MaxTRESPerJob%40
```
**El más importante para decidir qué partición pedir** (descubierto 2026-10-11): límites reales de recursos *por job* de cada QOS/partición — `cpu=`, `gres/gpu=` (cuántas GPUs permite un solo job), `mem=`, `node=`. En este clúster: `gpu-dev` solo permite 1 GPU por job (`gres/gpu` efectivamente 0-1) con `cpu=16`; **`gpu` permite 2 GPUs por job con `cpu=160`** (la que usa este documento para los 3 servicios); `gpu-max` permite 4 GPUs con `cpu=128`; `multinodo` permite 2 GPUs pero repartidas en 2 nodos (`node=2`, no sirve para este caso que necesita ambas GPUs en el mismo nodo). Hay una variante `format=Name,MaxTRESPerUser%40` (sin la `Job`) para el tope acumulado por *usuario* en vez de por *job* — son límites distintos y ambos pueden bloquear un `salloc` con mensajes de error diferentes (`QOSMaxGRESPerJob` vs `QOSMaxCpuPerUserLimit`).

```bash
sinfo -p gpu
```
Estado de los nodos de la partición `gpu` (la que se usa ahora, 2 GPUs por job): `idle` (libres), `mix` (parcialmente ocupados) o `alloc` (llenos). Cambiar `gpu` por `gpu-dev` si alguna vez vuelves al diseño de 1 sola GPU.

```bash
scontrol show partition gpu
```
Detalle de la partición: tiempo máximo de reserva, límites de CPU/memoria, y el total de GPUs configuradas.

```bash
sinfo -o '%P %N %G'
```
Lista cada partición, sus nodos, y los tipos exactos de GRES (GPU) configurados.

```bash
squeue -u francisco.higuera__ute.edu.ec
```
Tus propias reservas activas, con `JOBID` y `NODELIST`.

```bash
scontrol show job <JOBID>
```
Detalle de una reserva específica — nodo asignado, tiempo restante, recursos otorgados, y el usuario real que la lanzó (útil para confirmar si un job visto en `squeue` es tuyo o de alguien con nombre parecido).

```bash
sinfo -N -o "%N %C %O" -p gpu
```
**Carga real de CPU por nodo** (descubierto el 2026-10-11, cuando `vLLM` tardó 10+ minutos sin error en `compute-0-1`): `%C` son los CPUs asignados/libres/otros/totales de cada nodo, `%O` es su `CPU_LOAD` (promedio de carga). Si un nodo tiene `CPU_LOAD` muy por encima del otro (p. ej. 87 contra 26), significa que **otros usuarios** tienen trabajos ajenos saturando ese nodo — nada que ver con tu propia reserva, pero sí explica una importación de `torch` anormalmente lenta (es un cuello de botella de CPU/I-O, no de GPU: revisa con `nvidia-smi` si tu proceso ya está tocando la GPU o sigue atascado antes de eso). Nota: `compute-0-1` y `compute-0-2` son los mismos nodos físicos sin importar la partición (`gpu-dev`, `gpu`, `cpu`, etc. son solo políticas de acceso distintas sobre el mismo hardware) — la carga que veas aplica igual sin importar con qué partición consultes. Si un nodo está claramente más cargado, cancela (`scancel <JOBID>`) y vuelve a reservar apuntando al nodo más libre:
```bash
salloc -p gpu -n 1 -c 20 --mem=48G --gres=gpu:a100-sxm4-40gb:2 --time=04:00:00 --nodelist=<nodo-mas-libre>
```

---

## 10. Opción B — todo en una sola pestaña (alternativa a las secciones 1-6, recomendada con 3 servicios)

Mismo resultado que las 6 pestañas de arriba, pero con los 6 procesos en segundo plano dentro de **una única conexión** al nodo. Con 3 servicios en vez de 2, esta es ahora la forma más cómoda de gestionarlo — no es menos robusta: `nohup` (ignora el `SIGHUP` que manda cerrar la terminal) + `disown` (lo saca de la lista de trabajos de la shell, que si no también lo mataría al salir) hacen que los 6 procesos sigan vivos **aunque cierres esta pestaña por error**, mientras la reserva de Slurm (el job) siga activa. Lo único que de verdad los mata a todos es que termine el job (`scancel` o que se acabe el `--time`), exactamente igual que con 6 pestañas.

```bash
ssh francisco.higuera__ute.edu.ec@hpc.cedia.edu.ec
salloc -p gpu -n 1 -c 20 --mem=48G --gres=gpu:a100-sxm4-40gb:2 --time=04:00:00
```
Anota el `JOBID` y el `NODO` que te asigne (igual que en la sección 1).
```bash
srun --jobid=<JOBID> --pty bash
```

Ya dentro del nodo, los 3 servicios de un tirón (los contenedores `vllm-server`/`tei-server`/`vllm-vl-server` deben existir ya — ver secciones 1.1, 2.1 y 3.1 si es la primera vez):

```bash
CUDA_VISIBLE_DEVICES=0 nohup enroot start --mount $HOME --root --rw vllm-server \
  Qwen/Qwen2.5-7B-Instruct --port 8001 --max-model-len 4096 \
  > ~/vllm.log 2>&1 &
disown

nohup enroot start --mount $HOME --root --rw --env HF_ENDPOINT=https://huggingface.co tei-server \
  --model-id intfloat/multilingual-e5-large --port 8002 \
  > ~/tei.log 2>&1 &
disown

CUDA_VISIBLE_DEVICES=1 nohup enroot start --mount $HOME --root --rw vllm-vl-server \
  Qwen/Qwen2.5-VL-7B-Instruct --port 8003 --max-model-len 8192 --trust-remote-code \
  > ~/vllm-vl.log 2>&1 &
disown

nohup ssh -i ~/.ssh/hpc_tunnel_key -N -R 8765:localhost:8001 deploy@74.208.222.22 \
  > ~/tunnel_vllm.log 2>&1 &
disown

nohup ssh -i ~/.ssh/hpc_tunnel_key -N -R 8766:localhost:8002 deploy@74.208.222.22 \
  > ~/tunnel_tei.log 2>&1 &
disown

nohup ssh -i ~/.ssh/hpc_tunnel_key -N -R 8767:localhost:8003 deploy@74.208.222.22 \
  > ~/tunnel_vllm_vl.log 2>&1 &
disown
```

El prompt vuelve de inmediato después de cada bloque (a diferencia de la Opción A, donde los vLLM/TEI se quedan "colgados" en pantalla a propósito). Verificar que los 6 siguen corriendo:

```bash
jobs                    # lista los 6 procesos en segundo plano de esta shell
tail -f ~/vllm.log       # ver el progreso de arranque de vLLM (texto) en vivo
tail -f ~/vllm-vl.log    # ver el progreso del modelo de visión (Ctrl+C solo sale del tail, no mata el proceso)
curl http://localhost:8001/v1/models   # vLLM texto, una vez arriba
curl http://localhost:8002/health      # TEI, una vez arriba
curl http://localhost:8003/v1/models   # vLLM visión, una vez arriba
```

**Diferencia real con la Opción A**: en la Opción A, cerrar por error una de las 6 pestañas mata *solo* lo que corría ahí (el proceso en primer plano recibe el `SIGHUP`). En la Opción B, con una sola pestaña, el riesgo lógico sería que cerrarla matara los 6 procesos a la vez — pero `nohup`+`disown` evita exactamente eso: los 6 quedan desacoplados de la terminal, así que sobreviven a que la cierres. La única desventaja real es que ya no ves el log de cada servicio en pantalla por defecto (hay que `tail -f` el archivo correspondiente si quieres mirar el progreso).
