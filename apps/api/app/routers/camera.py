"""Camera router — handles camera frame analysis from browser."""

import logging
import uuid
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, HTTPException

from app.dependencies import FaceServiceDep, UserAuthDep, VisionServiceDep
from app.models.schemas import (
    CameraAnalysisResponse,
    CameraFrameRequest,
    FaceDetectionResult,
    StandardResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/camera", tags=["camera"])


@router.post("/analyze", response_model=StandardResponse[CameraAnalysisResponse])
async def analyze_camera_frame(
    body: CameraFrameRequest,
    current_user: UserAuthDep,
    vision_service: VisionServiceDep,
    face_service: FaceServiceDep,
) -> StandardResponse[CameraAnalysisResponse]:
    """Analyze a camera frame from the browser.

    Processes the frame for:
    - Face detection and identification
    - Visual scene analysis
    """
    try:
        # Decode base64 image
        import base64

        image_data = base64.b64decode(body.image)

        # Perform face detection
        import asyncio

        face_result = await asyncio.to_thread(face_service.detect_faces, image_data)

        # Perform visual analysis using vision service
        from io import BytesIO
        import tempfile
        from PIL import Image

        img = Image.open(BytesIO(image_data))

        # Use vision service for description
        visual_description = ""
        try:
            # Save to temp file for vision service
            with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
                img.save(tmp, format="JPEG")
                tmp_path = Path(tmp.name)
            try:
                description = await vision_service.analyze_image(
                    image_path=tmp_path,
                    prompt="Describe what you see in this image concisely.",
                )
                visual_description = description if description else ""
            finally:
                tmp_path.unlink(missing_ok=True)
        except Exception as e:
            logger.warning(f"Vision analysis failed: {e}")
            visual_description = ""

        # Build face detection result
        identified_faces = []
        if face_result and face_result.get("matches"):
            for match in face_result["matches"]:
                identified_faces.append(
                    {
                        "user_id": match.get("user_id", ""),
                        "name": match.get("name", "Unknown"),
                        "confidence": match.get("score", 0.0),
                    }
                )

        face_detection = FaceDetectionResult(
            faces_found=len(identified_faces),
            identified=identified_faces,
        )

        response = CameraAnalysisResponse(
            face_detection=face_detection,
            visual_analysis={
                "description": visual_description,
                "scene_type": "indoor" if visual_description else "unknown",
            },
            timestamp=datetime.utcnow(),
        )

        return StandardResponse(
            success=True,
            message="Frame analyzed successfully",
            data=response,
        )

    except Exception as e:
        logger.exception("Camera frame analysis failed")
        raise HTTPException(status_code=500, detail="Camera analysis failed")
