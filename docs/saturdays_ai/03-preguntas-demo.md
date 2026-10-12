# Preguntas de ejemplo para el Chat de Normativa (Demo Day)

Preguntas probadas en vivo contra producción (modelo `Qwen2.5-14B-Instruct`, embeddings reales vía TEI, 896 fragmentos indexados). Organizadas por lo que cada una demuestra — elige 3-4 según el tiempo que tengas (la demo completa son 4 minutos).

## 1. Cita correcta y precisa (lo más seguro para abrir)

> **¿Cuántas faltas puedo tener antes de reprobar por inasistencia?**

Cita el **Artículo 42** del Reglamento del Estudiante (70% de asistencia mínima) y razona explícitamente que la normativa habla en porcentaje, no en número de faltas — muestra que no solo recupera texto, lo interpreta. Ya verificada en vivo, ver `00-plan.md` §13.

> **¿Qué tipos de matrícula existen en la UTE?**

Cita el **Artículo 71** (y de paso el 13/14) del Reglamento del Estudiante, con la lista real (ordinaria, extraordinaria, especial...).

> **¿En qué casos puedo pedir la recalificación de un examen?**

Cita el **Artículo 40** del Reglamento del Estudiante.

## 2. Honestidad ante lo que NO cubre la normativa (el momento más importante de la demo)

> **¿Cuál es la capital de Ecuador?**

El sistema responde explícitamente: *"Los fragmentos consultados no cubren este tema; respondo con conocimiento general, no verificado contra la normativa indexada"* — y después sí contesta (Quito), dejando clarísima la frontera entre lo verificado y lo que no. **Este es el momento para señalar al jurado que el sistema no inventa cumplimiento normativo que no existe.**

## 3. Razonamiento sobre un caso ambiguo (para una pregunta del jurado, si preguntan "¿y si no está exactamente cubierto?")

> **¿Qué becas deportivas internacionales ofrece la UTE?**

No hay un artículo que lo responda directamente, pero el sistema encuentra artículos *relacionados* (becas en general, Art. 8 del Reglamento del Estudiante y Art. 77 de la LOES) y es transparente: dice que no se menciona específicamente, y que "se puede inferir" a partir de esos artículos — ni inventa un artículo que no existe, ni se cierra en un "no sé" improductivo.

## Otras preguntas con cita esperada (de respaldo, no probadas en vivo pero ancladas en el corpus — ver `scripts/rag/data/eval_set.jsonl`)

- ¿Qué principios debe garantizar el sistema de evaluación estudiantil? → Art. 35
- ¿Cómo se clasifican los tipos de evaluación de los aprendizajes? → Art. 36
- ¿Cuál es la escala de calificación y el promedio mínimo para aprobar? → Art. 37
- ¿Quiénes tienen derecho a la evaluación remedial? → Art. 38
- ¿Qué debe hacer el director de carrera si un docente no registra calificaciones a tiempo? → Art. 41
- ¿A quiénes aplica el instructivo de segunda lengua de la UTE? → Instructivo Segunda Lengua, Art. 1

## Recomendación de guion (4 minutos de demo)

1. Validar un sílabo real (texto o `.docx`) — 1 min.
2. Pregunta de la sección 1 en el chat — 1 min.
3. **Pregunta de la sección 2 (capital de Ecuador o similar) — el momento clave, no te la saltes.** — 1 min.
4. Pedir una pista al tutor IA en una práctica cualquiera (muestra que el mismo HPC también sirve al tutor) — 1 min.
