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


def _saturation_mask(pixels: np.ndarray) -> np.ndarray:
    channel_max = pixels.max(axis=-1).astype(np.int16)
    channel_min = pixels.min(axis=-1).astype(np.int16)
    return (channel_max - channel_min) > SATURATION_THRESHOLD


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

    areas = _label_components(mask)
    regions = [a for a in areas if a >= min_area]

    details = {
        "image_size": list(image.size),
        "region_count_before_filter": len(areas),
        "region_areas": sorted(regions, reverse=True),
        "min_region_area": min_area,
    }
    return len(regions), details
