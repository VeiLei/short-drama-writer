"""Jimeng image provider — delegates to Jimeng46Adapter."""

from app.image_providers.jimeng46_adapter import jimeng as _jimeng


async def generate_image(prompt: str, aspect_ratio: str = "9:16",
                         reference_images: list[str] = None) -> dict:
    """Generate an image via Jimeng 4.6. Returns {image_url, task_id, ...}."""
    result = await _jimeng.generate(prompt, aspect_ratio, reference_images=reference_images)
    return {
        "task_id": result.image_id,
        "status": "done",
        "image_url": result.image_url,
        "dimensions": result.dimensions,
        "aspect_ratio": result.aspect_ratio,
    }
