"""Jimeng 4.6 image generation provider."""

import httpx
from .base import ImageProvider, GenerateResult


class JimengProvider(ImageProvider):
    def __init__(self, api_key: str, api_secret: str):
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = "https://visual.volcengineapi.com"

    async def generate_image(self, prompt: dict) -> GenerateResult:
        positive = prompt.get("positive", "")
        negative = prompt.get("negative", "")
        width = prompt.get("width", 1080)
        height = prompt.get("height", 1920)

        payload = {
            "req_key": "jimeng_highres_v46",
            "prompt": positive,
            "negative_prompt": negative,
            "width": width,
            "height": height,
            "return_url": True,
        }

        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(
                f"{self.base_url}/submit",
                json=payload,
                headers={"Authorization": f"Bearer {self.api_key}"},
            )
            data = resp.json()
            if data.get("code") != 10000:
                return GenerateResult(
                    task_id="", status="failed", error=data.get("message", "Unknown error")
                )
            return GenerateResult(
                task_id=data.get("data", {}).get("task_id", ""),
                status="pending",
            )

    async def get_status(self, task_id: str) -> GenerateResult:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                f"{self.base_url}/query",
                json={"req_key": "jimeng_highres_v46", "task_id": task_id},
                headers={"Authorization": f"Bearer {self.api_key}"},
            )
            data = resp.json()
            if data.get("code") != 10000:
                return GenerateResult(task_id=task_id, status="failed", error=data.get("message"))
            status = data.get("data", {}).get("status", "unknown")
            file_url = data.get("data", {}).get("image_urls", [None])[0]
            return GenerateResult(
                task_id=task_id,
                status=status,
                file_url=file_url,
            )
