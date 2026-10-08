"""Regla de conteo explicita para circulos de papel de colores: cuenta regiones
de color saturado sobre fondo claro mediante componentes conexas, sin modelo
entrenado. Es la implementacion de referencia local (MockAIAdapter); un
proveedor real de vision (AnthropicAdapter) puede reemplazarla aplicando la
misma regla con un modelo."""

import io
from typing import Any

import numpy as np
from PIL import Image

MAX_DIMENSION = 256
SATURATION_THRESHOLD = 40  # max(R,G,B) - min(R,G,B); separa color de fondo neutro
MIN_REGION_AREA_RATIO = 0.0015  # descarta ruido: evita contar un "centro" sin area
MIN_COLOR_RATIO_TO_JUDGE_BLUR = 0.01  # por debajo de esto no hay color suficiente
# para juzgar nitidez: es una escena vacia, no una imagen borrosa (no son lo mismo
# para la regla de la guia: "vacia" cuenta 0 sin advertencia, "borrosa" es ilegible)
BLUR_VARIANCE_THRESHOLD = 60.0  # var(laplaciano) por debajo de esto, habiendo color
# presente: bordes demasiado suaves para distinguir centros con confianza


def _saturation_mask(pixels: np.ndarray) -> np.ndarray:
    channel_max = pixels.max(axis=-1).astype(np.int16)
    channel_min = pixels.min(axis=-1).astype(np.int16)
    return (channel_max - channel_min) > SATURATION_THRESHOLD


def _is_blurry(pixels: np.ndarray, mask: np.ndarray) -> tuple[bool, float]:
    """Laplaciano discreto (4-vecinos) sobre la escala de grises, vectorizado con
    numpy (sin scipy/cv2): una imagen nitida tiene bordes marcados y por lo tanto
    alta varianza; una imagen borrosa suaviza esos bordes y baja la varianza. Solo
    se evalua cuando hay suficiente color presente (ver MIN_COLOR_RATIO_TO_JUDGE_BLUR)
    para no confundir una escena vacia con una imagen borrosa."""
    if mask.mean() < MIN_COLOR_RATIO_TO_JUDGE_BLUR:
        return False, 0.0
    gray = pixels.mean(axis=-1)
    center = gray[1:-1, 1:-1]
    laplacian = 4 * center - gray[:-2, 1:-1] - gray[2:, 1:-1] - gray[1:-1, :-2] - gray[1:-1, 2:]
    variance = float(laplacian.var())
    return variance < BLUR_VARIANCE_THRESHOLD, variance


def _label_components(mask: np.ndarray) -> list[int]:
    """Etiquetado de componentes conexas (4-vecinos) con pila explicita, sin scipy."""
    height, width = mask.shape
    visited = np.zeros_like(mask, dtype=bool)
    areas: list[int] = []

    for y in range(height):
        for x in range(width):
            if not mask[y, x] or visited[y, x]:
                continue
            area = 0
            stack = [(y, x)]
            visited[y, x] = True
            while stack:
                cy, cx = stack.pop()
                area += 1
                for ny, nx in ((cy - 1, cx), (cy + 1, cx), (cy, cx - 1), (cy, cx + 1)):
                    if (
                        0 <= ny < height
                        and 0 <= nx < width
                        and mask[ny, nx]
                        and not visited[ny, nx]
                    ):
                        visited[ny, nx] = True
                        stack.append((ny, nx))
            areas.append(area)
    return areas


def count_colored_regions(image_bytes: bytes) -> tuple[int, dict[str, Any]]:
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    image.thumbnail((MAX_DIMENSION, MAX_DIMENSION))
    pixels = np.asarray(image)

    mask = _saturation_mask(pixels)
    total_pixels = mask.shape[0] * mask.shape[1]
    min_area = max(4, int(total_pixels * MIN_REGION_AREA_RATIO))

    illegible, blur_variance = _is_blurry(pixels, mask)
    areas = _label_components(mask)
    regions = [] if illegible else [a for a in areas if a >= min_area]

    details = {
        "image_size": list(image.size),
        "region_count_before_filter": len(areas),
        "region_areas": sorted(regions, reverse=True),
        "min_region_area": min_area,
        "illegible": illegible,
        "blur_variance": round(blur_variance, 2),
    }
    return len(regions), details
