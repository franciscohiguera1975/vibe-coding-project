"""Las 4 practicas iniciales (Prompt Maestro §17): 2 de desarrollo de software y 2 de
manejo de imagenes (regla §37: contenido derivado de material pedagogico propio, no de
ejemplos genericos).

Nota interna (no citar en campos visibles al estudiante): software-01/image-01
construyen un prototipo completo; software-02/image-02 extienden ese mismo prototipo
como ejercicio de depuracion/diagnostico sobre sus propios criterios de aceptacion.
"""

from typing import Any

INITIAL_PRACTICES: list[dict[str, Any]] = [
    {
        "slug": "software-01-simulacion-mru",
        "title": "Simulación de movimiento rectilíneo uniforme",
        "type": "software",
        "category_slug": "desarrollo-de-software",
        "difficulty": "beginner",
        "estimated_time_minutes": 45,
        "technologies": ["javascript", "html", "css"],
        "tags": ["vibe-coding", "fisica-mru", "simulacion"],
        "objectives": [
            "Construir con asistencia de IA una actividad interactiva de predicción y verificación",
            "Expresar un modelo físico explícito (distancia = velocidad × tiempo) en código, no en texto generado por el modelo de lenguaje",
            "Aplicar la secuencia predecir → ajustar → ejecutar → observar → explicar",
        ],
        "description": (
            "Construya, paso a paso y con ayuda de IA, una actividad de navegador donde "
            "el estudiante predice la distancia recorrida a velocidad constante, ajusta "
            "velocidad y tiempo, y compara su predicción con el resultado calculado."
        ),
        "instructions": (
            "Construya la actividad en cinco pasos. (1) Escriba el objetivo y los "
            "supuestos: viaje a velocidad constante, distancia = velocidad × tiempo, "
            "velocidad entre 0 y 100 km/h, tiempo entre 0 y 3 horas; aceleración, "
            "tráfico y paradas quedan fuera del modelo. (2) Implemente la secuencia fija "
            "predecir → ajustar → ejecutar → observar → explicar: no se puede ajustar "
            "sin haber predicho antes. (3) Construya los controles (deslizadores o "
            "campos con unidades visibles, accesibles por teclado, con botón de "
            "reinicio) y calcule la distancia en código, nunca estimada por el modelo de "
            "lenguaje. (4) Muestre el resultado numérico con su equivalente textual y "
            "una retroalimentación que compare la predicción del estudiante con el "
            "resultado calculado. (5) Verifique los tres ejemplos numéricos y responda "
            "la pregunta de transferencia con valores nuevos."
        ),
        "content": {
            "model": {
                "formula": "distance_km = speed_kmh * time_h",
                "variables": {
                    "speed_kmh": {"label": "Velocidad", "unit": "km/h", "min": 0, "max": 100},
                    "time_h": {"label": "Tiempo", "unit": "h", "min": 0, "max": 3},
                },
                "assumptions": ["velocidad constante", "sin aceleración, tráfico ni paradas"],
            },
            "sequence": ["predict", "adjust", "execute", "observe", "explain"],
            "worked_examples": [
                {"speed_kmh": 60, "time_h": 2, "distance_km": 120},
                {"speed_kmh": 40, "time_h": 1.5, "distance_km": 60},
                {"speed_kmh": 0, "time_h": 2, "distance_km": 0},
            ],
            "transfer_question": "¿Cuánto tiempo se necesita a 80 km/h para recorrer 200 km?",
            "reflection_questions": [
                "¿Qué relación observa entre el tiempo y la distancia cuando la velocidad es constante?",
                "¿Qué pasaría con la representación visual si la velocidad se duplicara?",
            ],
        },
        "evaluation": {
            "strategy": "numeric_match",
            "checks": [
                {"field": "distance_km_case1", "expected": 120, "tolerance": 0.01},
                {"field": "distance_km_case2", "expected": 60, "tolerance": 0.01},
                {"field": "distance_km_case3", "expected": 0, "tolerance": 0.01},
            ],
        },
        "ai_configuration": {"hints_enabled": True, "hint_context": "modelo de MRU"},
        "embedding_configuration": {"embeddable": True, "layout": "standalone"},
        "metadata": {},
        "status": "published",
    },
    {
        "slug": "software-02-depuracion-mru",
        "title": "Depuración de una simulación generada por IA",
        "type": "software",
        "category_slug": "desarrollo-de-software",
        "difficulty": "intermediate",
        "estimated_time_minutes": 40,
        "technologies": ["javascript", "html"],
        "tags": ["vibe-coding", "fisica-mru", "depuracion", "evaluacion-de-codigo"],
        "objectives": [
            "Analizar código generado por IA contra una especificación escrita",
            "Detectar y corregir errores de validación de límites y de accesibilidad",
            "Usar los criterios de aceptación de la práctica base como pruebas de regresión",
        ],
        "description": (
            "A partir de una versión con errores intencionales de la simulación de MRU "
            "(practica software-01), identifique y corrija los fallos usando sus "
            "criterios de aceptación como referencia de corrección."
        ),
        "instructions": (
            "Se le entrega una versión de la simulación de MRU con tres fallos "
            "intencionales (ver `content.buggy_version_description`). Pida ayuda a un "
            "asistente de IA para localizarlos, pero verifique cada corrección usted "
            "mismo contra los criterios de aceptación de `content.acceptance_criteria`: "
            "un cambio que 'parece funcionar' no es suficiente si no pasa los cuatro "
            "casos. Entregue el código corregido y una nota breve de qué causaba cada "
            "fallo."
        ),
        "content": {
            "based_on": "software-01-simulacion-mru",
            "buggy_version_description": {
                "bug_1": "El formulario acepta velocidades negativas y las usa en el cálculo sin mostrar error.",
                "bug_2": "Cuando tiempo = 0, el código muestra 'NaN km' en vez de 0 km.",
                "bug_3": "Los controles de velocidad y tiempo solo responden al mouse; no son operables con teclado.",
            },
            "acceptance_criteria": [
                "40 km/h durante 1.5 horas deben producir 60 km",
                "Tiempo 0 debe producir distancia 0",
                "Un valor negativo debe generar un error claro, no un resultado",
                "La actividad debe poder completarse solo con teclado",
            ],
        },
        "evaluation": {
            "strategy": "numeric_match",
            "checks": [
                {"field": "distance_km_check", "expected": 60, "tolerance": 0.01},
                {"field": "zero_time_distance", "expected": 0, "tolerance": 0.01},
                {"field": "negative_speed_rejected", "expected": 1, "tolerance": 0},
                {"field": "keyboard_accessible", "expected": 1, "tolerance": 0},
            ],
        },
        "ai_configuration": {"hints_enabled": True},
        "embedding_configuration": {"embeddable": True, "layout": "standalone"},
        "metadata": {
            "extends": "software-01-simulacion-mru",
        },
        "status": "published",
    },
    {
        "slug": "image-01-conteo-circulos",
        "title": "Prototipo de conteo de círculos de papel",
        "type": "image",
        "category_slug": "manejo-de-imagenes",
        "difficulty": "beginner",
        "estimated_time_minutes": 50,
        "technologies": ["python", "html"],
        "tags": ["imagenes", "conteo-objetos", "conteo", "vision"],
        "objectives": [
            "Construir un prototipo de conteo de objetos con una regla explícita",
            "Comparar el conteo propuesto contra una referencia humana",
            "Reconocer los límites de lo que un modelo puede inferir de una imagen",
        ],
        "description": (
            "Construya un prototipo que cuente círculos de papel de colores en imágenes "
            "con una regla explícita, mostrando el conteo propuesto y una advertencia "
            "visible ante imágenes ilegibles."
        ),
        "instructions": (
            "Construya el prototipo en cinco pasos. (1) Escriba la regla de conteo con "
            "sus cuatro partes: qué cuenta (un círculo cuyo centro es visible), qué no "
            "cuenta (sin centro visible, reflejos, sombras), cuándo la imagen es "
            "ilegible (desenfoque que impide ver los centros) y qué se conserva siempre "
            "(identificador, versión del método, resultado por imagen). (2) Prepare una "
            "referencia humana con al menos dos etiquetadores independientes; concilie "
            "los desacuerdos antes de probar. (3) Divida las imágenes en 12 de "
            "desarrollo y 8 reservadas para la prueba; las fotografías casi idénticas "
            "permanecen en el mismo grupo. (4) Construya el visor (imagen, conteo "
            "propuesto, confianza, advertencia, versión del método) y pruébelo con las "
            "12 imágenes de desarrollo. (5) Ejecute el método definitivo una sola vez "
            "sobre las 8 imágenes reservadas y redacte el informe de errores."
        ),
        "content": {
            "counting_rule": {
                "counts": "un círculo cuyo centro es visible",
                "excludes": ["círculos sin centro visible", "reflejos", "sombras"],
                "illegible_when": ["desenfoque que impide ver los centros"],
                "always_preserved": [
                    "identificador de la imagen",
                    "versión del método",
                    "resultado por imagen",
                ],
            },
            "dataset": {"development_images": 12, "reserved_test_images": 8},
            "required_result_fields": [
                "id",
                "conteo_propuesto",
                "confianza",
                "advertencia",
                "version_metodo",
            ],
        },
        "evaluation": {
            "strategy": "count_comparison",
            "reference": {
                "img-13": 5,
                "img-14": 0,
                "img-15": 3,
                "img-16": 7,
                "img-17": 2,
                "img-18": 4,
                "img-19": 6,
                "img-20": 1,
            },
            "passing_score": 75,
        },
        "ai_configuration": {"strategy": "analyze_image", "uses_ai_provider": True},
        "embedding_configuration": {"embeddable": True, "layout": "standalone"},
        "metadata": {
            "note": (
                "La referencia de conteo es un marcador de posición de ejemplo; cargue su "
                "propio conjunto de 20 imágenes y su referencia.csv vía el panel de "
                "administración antes de un uso evaluativo real."
            ),
        },
        "status": "published",
    },
    {
        "slug": "image-02-diagnostico-errores",
        "title": "Diagnóstico de errores de conteo",
        "type": "image",
        "category_slug": "manejo-de-imagenes",
        "difficulty": "intermediate",
        "estimated_time_minutes": 35,
        "technologies": ["python"],
        "tags": ["imagenes", "conteo-objetos", "analisis-de-errores"],
        "objectives": [
            "Interpretar patrones de error de un método de conteo (iluminación, superposición, desenfoque)",
            "Proponer un ajuste a la regla de conteo a partir de evidencia",
        ],
        "description": (
            "Usando los resultados de 'Prototipo de conteo de círculos de papel' "
            "(image-01), clasifique los errores de las 8 imágenes reservadas por "
            "condición difícil y proponga un ajuste a la regla de conteo."
        ),
        "instructions": (
            "Parta del informe de errores del paso 5 de la práctica image-01: compare "
            "cada conteo propuesto con la referencia humana en las 8 imágenes "
            "reservadas. Clasifique cada error por condición (iluminación, "
            "superposición o desenfoque), anote al menos dos errores con una "
            "explicación de su causa probable, y proponga un ajuste concreto a la "
            "regla de conteo (sin ejecutar aún la prueba reservada de nuevo: cambiar "
            "la regla invalida esa prueba y exige un nuevo conjunto reservado)."
        ),
        "content": {
            "based_on": "image-01-conteo-circulos",
            "error_conditions": ["iluminacion", "superposicion", "desenfoque"],
            "required_output": [
                "tabla de error por condición",
                "al menos dos errores anotados con explicación",
                "una propuesta de ajuste a la regla",
            ],
        },
        "evaluation": {"strategy": "manual"},
        "ai_configuration": {"hints_enabled": True},
        "embedding_configuration": {"embeddable": True, "layout": "standalone"},
        "metadata": {
            "extends": "image-01-conteo-circulos",
        },
        "status": "published",
    },
]
