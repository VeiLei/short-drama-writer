"""即梦 4.6 图片生成适配器（异步 submit→poll 模式，火山引擎 AK/SK 签名认证）"""

import json
import asyncio
import logging
from typing import Optional, List

import httpx
import tenacity

from .base import BaseImageProvider, ImageResult
from .volc_auth import get_signed_headers
from app.config import config

logger = logging.getLogger(__name__)


class Jimeng46Adapter(BaseImageProvider):
    """即梦 4.6 图片生成适配器。"""

    ASPECT_RATIO_PIXELS = {
        "16:9": {"width": 2560, "height": 1440},
        "9:16": {"width": 1440, "height": 2560},
        "1:1": {"width": 2048, "height": 2048},
        "3:4": {"width": 1728, "height": 2304},
        "4:3": {"width": 2304, "height": 1728},
    }

    def __init__(self):
        self.ak = config.JIMENG_API_KEY
        self.sk = config.JIMENG_API_SECRET
        self.host = "https://visual.volcengineapi.com"
        self.region = "cn-north-1"
        self.service = "cv"
        self.timeout = httpx.Timeout(300.0, connect=30.0)
        self._submit_lock = asyncio.Semaphore(1)

    def _get_signed_headers(self, method: str, path: str, body: str = "") -> dict:
        host_for_sign = self.host.replace("https://", "").replace("http://", "")
        return get_signed_headers(
            method=method, host=host_for_sign, path=path, body=body,
            ak=self.ak, sk=self.sk, region=self.region, service=self.service,
        )

    @tenacity.retry(
        stop=tenacity.stop_after_attempt(3),
        wait=tenacity.wait_exponential(min=2, max=30),
        retry=tenacity.retry_if_exception_type(
            (httpx.HTTPStatusError, httpx.ProtocolError, TimeoutError, httpx.TimeoutException)
        ),
        reraise=True,
    )
    async def generate(
        self,
        prompt: str,
        aspect_ratio: str = "1:1",
        reference_images: Optional[List[str]] = None,
        force_single: bool = True,
        **kwargs,
    ) -> ImageResult:
        async with self._submit_lock:
            task_id = await self._submit_task(prompt, aspect_ratio, reference_images, force_single, **kwargs)
        return await self._poll_task(task_id, aspect_ratio)

    async def _submit_task(
        self, prompt: str, aspect_ratio: str,
        reference_images: Optional[List[str]], force_single: bool, **kwargs
    ) -> str:
        path = "/?Action=CVSync2AsyncSubmitTask&Version=2022-08-31"
        payload = {
            "req_key": "jimeng_seedream46_cvtob",
            "prompt": prompt,
            "force_single": force_single,
        }

        size = kwargs.get("size", None)
        if size is not None:
            payload["size"] = size
        else:
            dims = self.ASPECT_RATIO_PIXELS.get(aspect_ratio, {"width": 4096, "height": 4096})
            payload["width"] = dims["width"]
            payload["height"] = dims["height"]

        for key in ("scale", "min_ratio", "max_ratio"):
            if key in kwargs:
                payload[key] = kwargs[key]

        if reference_images:
            payload["image_urls"] = reference_images[:14]

        body = json.dumps(payload)
        logger.info("[Jimeng46] Submit - prompt_len=%d image_urls=%d",
                     len(prompt), len(reference_images or []))
        headers = self._get_signed_headers("POST", path, body)
        headers["Content-Type"] = "application/json"

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(f"{self.host}{path}", content=body, headers=headers)
            if response.status_code != 200:
                logger.error("[Jimeng46] Submit error - status=%s body=%s",
                             response.status_code, response.text[:500])
            response.raise_for_status()
            data = response.json()

        if data.get("code") != 10000:
            logger.error("[Jimeng46] Submit failed - code=%s message=%s",
                         data.get("code"), data.get("message"))
            raise ValueError(f"Jimeng46 submit failed: {data.get('message')}")
        return data["data"]["task_id"]

    async def _poll_task(self, task_id: str, aspect_ratio: str) -> ImageResult:
        path = "/?Action=CVSync2AsyncGetResult&Version=2022-08-31"
        payload = {"req_key": "jimeng_seedream46_cvtob", "task_id": task_id}
        body = json.dumps(payload)
        headers = self._get_signed_headers("POST", path, body)
        headers["Content-Type"] = "application/json"

        max_attempts = 60
        for attempt in range(max_attempts):
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(f"{self.host}{path}", content=body, headers=headers)
                if response.status_code != 200:
                    try:
                        err_data = response.json()
                        err_msg = err_data.get("message", response.text[:200])
                    except Exception:
                        err_msg = response.text[:200]
                    raise ValueError(f"Jimeng46 poll failed (HTTP {response.status_code}): {err_msg}")
                data = response.json()

            # code != 10000 时 data 为 null（见接口文档：优先判断 code=10000, 然后再判断data.status）
            if data.get("code") != 10000:
                logger.warning("[Jimeng46] Poll attempt %d returned code=%s message=%s",
                             attempt + 1, data.get("code"), data.get("message"))
                await asyncio.sleep(10)
                continue

            result_data = data.get("data")
            if result_data is None:
                logger.warning("[Jimeng46] Poll attempt %d returned null data, retrying", attempt + 1)
                await asyncio.sleep(10)
                continue

            status = result_data.get("status", "")
            if status == "done":
                image_urls = result_data.get("image_urls", [])
                b64_data = result_data.get("binary_data_base64", [])
                image_url = image_urls[0] if image_urls else ""
                b64_str = b64_data[0] if b64_data else ""
                return ImageResult(
                    image_id=task_id,
                    image_url=image_url or (f"data:image/png;base64,{b64_str}" if b64_str else ""),
                    dimensions=f"{self.ASPECT_RATIO_PIXELS.get(aspect_ratio, {}).get('width', 4096)}x{self.ASPECT_RATIO_PIXELS.get(aspect_ratio, {}).get('height', 4096)}",
                    aspect_ratio=aspect_ratio,
                    api_response={
                        "code": data.get("code"),
                        "message": data.get("message"),
                        "request_id": data.get("request_id"),
                        "data": {"image_urls": image_urls, "status": result_data.get("status")},
                    },
                )
            elif status in ("failed", "expired", "not_found"):
                raise ValueError(f"Jimeng46 task {status}: {task_id}")
            else:
                if attempt == 0:
                    logger.info("[Jimeng46] Polling task %s, status=%s", task_id, status)
                await asyncio.sleep(10)

        raise TimeoutError(f"Jimeng46 polling timeout: {task_id}")

    async def refine(self, image_id: str, instruction: str) -> ImageResult:
        raise NotImplementedError("Jimeng46Adapter does not support refine()")


# Singleton
jimeng = Jimeng46Adapter()
