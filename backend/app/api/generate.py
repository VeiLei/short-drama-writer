"""Asset generation API routes."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/api/generate", tags=["generate"])


class ImageGenerateRequest(BaseModel):
    provider: str = "jimeng"
    prompt: dict


class VideoGenerateRequest(BaseModel):
    provider: str = "seedance"
    prompt: dict


@router.post("/image")
async def generate_image(req: ImageGenerateRequest):
    """Submit an image generation task."""
    if req.provider == "jimeng":
        from ..providers.jimeng import JimengProvider
        from ..config import config
        provider = JimengProvider(config.JIMENG_API_KEY, config.JIMENG_API_SECRET)
        result = await provider.generate_image(req.prompt)
        return {"task_id": result.task_id, "status": result.status}
    raise HTTPException(400, f"Unknown provider: {req.provider}")


@router.post("/video")
async def generate_video(req: VideoGenerateRequest):
    """Submit a video generation task."""
    # Stub — real implementation follows same pattern as image
    return {"task_id": "stub", "status": "pending"}


@router.get("/status/{task_id}")
async def get_status(task_id: str, provider: str = "jimeng"):
    """Query generation task status."""
    if provider == "jimeng":
        from ..providers.jimeng import JimengProvider
        from ..config import config
        p = JimengProvider(config.JIMENG_API_KEY, config.JIMENG_API_SECRET)
        result = await p.get_status(task_id)
        return {
            "task_id": result.task_id,
            "status": result.status,
            "file_url": result.file_url,
            "error": result.error,
        }
    return {"task_id": task_id, "status": "unknown"}
