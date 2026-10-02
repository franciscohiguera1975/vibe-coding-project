from typing import Any

from pydantic import BaseModel


class ImageAnalysisResponse(BaseModel):
    key: str
    url: str
    count: int
    warnings: list[str]
    details: dict[str, Any]
