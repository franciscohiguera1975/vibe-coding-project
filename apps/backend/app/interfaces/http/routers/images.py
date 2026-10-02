from fastapi import APIRouter, Depends, File, Form, UploadFile

from app.application.use_cases.images.analyze_image import AnalyzeImageUseCase
from app.application.use_cases.images.process_image import ProcessImageUseCase
from app.domain.entities.identity import User
from app.interfaces.http.dependencies.auth import get_current_user
from app.interfaces.http.dependencies.image_use_cases import (
    get_analyze_image_use_case,
    get_process_image_use_case,
)
from app.interfaces.http.schemas.image import ImageAnalysisResponse

router = APIRouter(prefix="/images", tags=["images"])


@router.post("/analyze", response_model=ImageAnalysisResponse)
async def analyze_image(
    practice_slug: str = Form(...),
    file: UploadFile = File(...),
    actor: User = Depends(get_current_user),
    process_use_case: ProcessImageUseCase = Depends(get_process_image_use_case),
    analyze_use_case: AnalyzeImageUseCase = Depends(get_analyze_image_use_case),
) -> ImageAnalysisResponse:
    file_bytes = await file.read()
    content_type = file.content_type or "application/octet-stream"

    processed = process_use_case.execute(
        filename=file.filename or "upload", content_type=content_type, file_bytes=file_bytes
    )
    result = analyze_use_case.execute(
        practice_slug=practice_slug, file_bytes=file_bytes, content_type=content_type
    )

    return ImageAnalysisResponse(
        key=processed.key,
        url=processed.url,
        count=result.count,
        warnings=result.warnings,
        details=result.details,
    )
