# Pasos a ejecutar en el HPC de CEDIA

Runbook para que el usuario ejecute en su propia sesión del HPC (`hpc.cedia.edu.ec`) — Claude Code no tiene acceso a ese servidor, así que estos pasos los corre la persona. Reescrito completo el 2026-10-09 tras descubrir que la cuenta tiene un límite de **1 sola reserva de Slurm activa a la vez** (`QOSMaxJobsPerUserLimit`) — el diseño anterior de "dos reservas independientes" no es viable aquí. Esta es la versión definitiva.

**Qué se arma**: **vLLM** (genera las respuestas, puerto `8001`) y **TEI** (calcula embeddings, puerto `8002`), los dos dentro de **una sola reserva de Slurm**, corriendo como dos procesos separados en el mismo nodo — se conecta a ese nodo por `ssh` directo para cada pieza adicional, sin volver a pasar por `salloc`/`srun` (eso es lo que evita el límite de 1 job). Cada uno se tunela por separado hacia el VPS. No es un servicio permanente: se levanta antes de usar la función de RAG (prueba o demo) y se apaga después (ver `00-plan.md` §5 para el porqué).

**4 pestañas de terminal en total, ninguna se cierra mientras dure la sesión:**

| Pestaña | Qué hace |
|---|---|
| 1 | La única reserva (`salloc`) + arranca **vLLM** |
| 2 | `ssh` directo al mismo nodo + arranca **TEI** |
| 3 | `ssh` directo al mismo nodo + túnel de vLLM (8001→8765) |
| 4 | `ssh` directo al mismo nodo + túnel de TEI (8002→8766) |

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

```bash
ssh francisco.higuera__ute.edu.ec@hpc.cedia.edu.ec
salloc -p gpu-dev -n 1 -c 10 --mem=24G --gres=gpu:a100-sxm4-40gb:1 --time=02:00:00
```

(`-c 10 --mem=24G`: un poco más que solo para vLLM, porque esta misma reserva también va a correr TEI al lado — ver sección 2. La GPU completa es solo para vLLM; TEI corre en CPU).

**Nota (descubierto 2026-10-09)**: los tipos MIG del Anexo 1 del manual (`a100_1g.5gb`, `a100_2g.10gb`, `a100_3g.20gb`) no están configurados en los nodos de `gpu-dev` — ahí solo existe el GPU completo `a100-sxm4-40gb`. Por eso se pide ese tipo exacto.

La salida muestra el `JOBID` y el nodo asignado — **anótalos, los necesitas para las otras 3 pestañas**:

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

### 1.2. Arrancar vLLM

```bash
enroot start --mount $HOME --root --rw vllm-server \
  Qwen/Qwen2.5-7B-Instruct \
  --port 8001 \
  --max-model-len 4096
```

**Importante**: la imagen `vllm/vllm-openai` tiene su `ENTRYPOINT` fijo en `vllm serve` — lo que le pases a `enroot start <contenedor> <comando>` se agrega como argumento a ese entrypoint, no lo reemplaza. No escribas `vllm serve ...` ni `python3 -m vllm.entrypoints...` delante del modelo (ambos rompen el comando) — el modelo y las opciones van directo, como arriba.

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

## 3. Pestaña 3 — túnel de vLLM

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

## 4. Pestaña 4 — túnel de TEI

Pestaña nueva, conectando otra vez al mismo nodo:

```bash
ssh francisco.higuera__ute.edu.ec@hpc.cedia.edu.ec
ssh NODO
curl http://localhost:8002/health
```

Abrir el túnel:

```bash
ssh -i ~/.ssh/hpc_tunnel_key -N -R 8766:localhost:8002 deploy@74.208.222.22
```

**No cerrar esta pestaña.** Los dos túneles (3 y 4) apuntan al mismo VPS con puertos remotos distintos (8765 y 8766) — no chocan entre sí aunque los dos salgan del mismo nodo.

---

## 5. Verificación y carga de datos (esto lo hace Claude Code, no tú)

Una vez las 4 pestañas están arriba:

1. Confirmar desde el VPS que ambos puertos tunelados responden (`curl http://localhost:8765/v1/models`, `curl http://localhost:8766/health`).
2. Configurar `RAG_BASE_URL=http://localhost:8765/v1` y `EMBEDDING_BASE_URL=http://localhost:8766` en el `.env` de producción.
3. Cargar los embeddings del corpus (solo hace falta la primera vez que el túnel queda arriba; es idempotente):
   ```bash
   cd /opt/vibe-coding-platform/apps/backend
   .venv/bin/python scripts/rag/load_chunks.py
   ```
   Guarda los vectores en **LanceDB**, embebido en el propio VPS (no en Postgres ni en el HPC — ver `00-plan.md` §5).
4. Probar las pantallas "Validación de sílabos" y "Evaluación" en la plataforma.

## Al terminar

En cada una de las 4 pestañas, `Ctrl+C` (para los túneles) o simplemente cerrar. Luego, en la Pestaña 1 (o desde cualquiera con `squeue -u francisco.higuera__ute.edu.ec`), liberar la única reserva:

```bash
scancel JOBID
```

Anota aquí la fecha y duración real de la sesión, para la diapositiva de "arquitectura y costos".

---

## 6. Si algo falla

- **Un `enroot start` de vLLM da `ModuleNotFoundError: No module named 'vllm'` (no el error de "modelo no válido")**: el contenedor quedó corrupto. Reconstruir desde cero:
  ```bash
  enroot remove vllm-server
  rm vllm+vllm-openai+latest.sqsh
  enroot import docker://vllm/vllm-openai:latest
  enroot create --name vllm-server vllm+vllm-openai+latest.sqsh
  ```
- **El túnel no conecta**: revisar que la llave pública sigue en `/home/deploy/.ssh/authorized_keys` del VPS.
- **vLLM no carga el modelo a tiempo**: hay respaldo — `RAG_LLM_PROVIDER` puede apuntar a GitHub Models (capa gratuita) cambiando una sola variable de entorno, sin tocar código. Vale la pena probarlo una vez antes del día de la demo.
- **La GPU pedida (`a100-sxm4-40gb`) no está disponible**: revisar `sinfo -p gpu-dev`; si está ocupado, la partición `interactive` con `a100_2g.10gb` es la alternativa más chica.
- **Un `salloc`/`srun` nuevo se queda en `PD` con razón `(QOSMaxJobsPerUserLimit)`**: tu cuenta solo permite **1 reserva activa a la vez** — no es falta de recursos del clúster, es un tope de tu cuenta. Por eso todo este documento usa una sola reserva compartida para los dos servicios (secciones 1-4) en vez de dos independientes. No intentar una segunda reserva mientras la primera siga activa.
- **Un `srun --jobid=...` se queda colgado o da `Job/step already completing or completed`**: estás tratando de crear un segundo "paso" en la misma reserva (`-n 1` solo da un cupo). Para cualquier conexión adicional al mismo nodo, usar `ssh <nodo>` directo, nunca `srun` otra vez.
- **Viste un `JOBID` de otro usuario con tu mismo nombre en `squeue`**: la columna `USER` se corta a 8 caracteres — puede coincidir con la de alguien más (pasó con `francisco.mendoza__yachaytech.edu.ec`, truncado igual que `francisco.higuera__ute.edu.ec`). Antes de cancelar un job que no reconoces, confirmar con `scontrol show job <JOBID>` (revisar el campo `Command`/`WorkDir`, ahí se ve el usuario real) — nunca cancelar un job que no sea tuyo.
- **Cerraste por error la pestaña de la Pestaña 1 (el `salloc`)**: la reserva murió, y con ella todo lo que corría adentro (vLLM y TEI). No hay que recuperarla — repetir desde la sección 1 (los contenedores y modelos siguen descargados, así que es rápido).

## 7. Comandos de diagnóstico (de consulta, no reservan ni cambian nada)

```bash
sinfo -p gpu-dev
```
Estado de los nodos de `gpu-dev`: `idle` (libres), `mix` (parcialmente ocupados) o `alloc` (llenos).

```bash
scontrol show partition gpu-dev
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
