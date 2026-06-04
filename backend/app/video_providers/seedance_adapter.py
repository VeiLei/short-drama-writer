"""Seedance 2.0 video generation adapter. Uses ARK SDK (API key auth)."""

import asyncio
import logging
from typing import Optional, List

from .base import BaseVideoProvider, VideoResult
from app.config import config

try:
    from volcenginesdkarkruntime import Ark
except ImportError:
    Ark = None

logger = logging.getLogger(__name__)


class SeedanceAdapter(BaseVideoProvider):
    """Doubao Seedance 2.0 video generation adapter."""

    MODEL_ID = "doubao-seedance-2-0-260128"

    def __init__(self):
        self.api_key = config.DOUBAO_SEEDANCE_API_KEY or config.ARK_API_KEY
        self.host = config.ARK_BASE_URL or "https://ark.cn-beijing.volces.com/api/v3"
        self._submit_lock = asyncio.Semaphore(1)

    def _get_client(self) -> "Ark":
        if Ark is None:
            raise RuntimeError(
                "volcenginesdkarkruntime is not installed. "
                "Run `pip install 'volcengine-python-sdk[ark]'`."
            )
        if not self.api_key:
            raise RuntimeError(
                "DOUBAO_SEEDANCE_API_KEY / ARK_API_KEY is not configured. "
                "Set it in backend/.env."
            )
        return Ark(base_url=self.host, api_key=self.api_key)

    async def create_task(
        self, prompt: str, reference_images: Optional[List[str]] = None,
        ratio: str = "16:9", duration: int = 10, **kwargs
    ) -> str:
        client = self._get_client()

        content = [{"type": "text", "text": prompt}]
        if reference_images:
            for ref in reference_images:
                content.append({
                    "type": "image_url",
                    "image_url": {"url": ref},
                    "role": "reference_image",
                })

        params = {
            "model": self.MODEL_ID,
            "content": content,
            "ratio": ratio,
            "duration": duration,
            "resolution": kwargs.pop("resolution", "1080p"),
            "generate_audio": kwargs.pop("generate_audio", True),
            "watermark": kwargs.pop("watermark", False),
            "return_last_frame": True,
        }

        def _create():
            return client.content_generation.tasks.create(**params)

        result = await asyncio.to_thread(_create)
        data = _serialize(result)
        task_id = data.get("id", "")
        if not task_id:
            raise ValueError(f"Seedance task creation failed: {data}")
        logger.info("Seedance task created: %s (ratio=%s duration=%ss)", task_id, ratio, duration)
        return task_id

    async def get_task_status(self, task_id: str) -> VideoResult:
        client = self._get_client()

        def _get():
            return client.content_generation.tasks.get(task_id=task_id)

        result = await asyncio.to_thread(_get)
        data = _serialize(result)

        status = data.get("status", "")
        content = data.get("content", {}) or {}
        video_url = content.get("video_url") or ""

        logger.info("Seedance poll: %s status=%s has_video=%s", task_id, status, bool(video_url))

        return VideoResult(
            video_id=task_id,
            video_url=video_url,
            duration=data.get("duration", duration) if video_url else 0,
            dimensions=content.get("dimensions", ""),
            aspect_ratio=data.get("ratio", "16:9"),
            api_response=data,
        )

    async def generate(
        self, prompt: str, reference_images: Optional[List[str]] = None,
        ratio: str = "16:9", duration: int = 10, **kwargs
    ) -> VideoResult:
        async with self._submit_lock:
            task_id = await self.create_task(prompt, reference_images, ratio, duration, **kwargs)

        for _ in range(120):
            result = await self.get_task_status(task_id)
            if result.video_url:
                return result
            if result.api_response.get("status") == "failed":
                err = result.api_response.get("error", {})
                raise ValueError(f"Video generation failed: {err.get('message', err)}")
            await asyncio.sleep(30)

        raise TimeoutError(f"Video generation timeout: {task_id}")


def _serialize(result) -> dict:
    if hasattr(result, "model_dump"):
        return result.model_dump()
    if hasattr(result, "dict"):
        return result.dict()
    if isinstance(result, dict):
        return result
    return {"raw": str(result)}


seedance = SeedanceAdapter()
