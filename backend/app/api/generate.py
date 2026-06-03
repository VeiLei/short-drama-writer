"""Asset generation API routes."""

import base64
import logging
from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.image_providers.jimeng46_adapter import jimeng as jimeng_provider
from app.utils.tos import upload_to_tos
from app.utils.asset_index import AssetIndex

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/generate", tags=["generate"])


# ── Request models ─────────────────────────────────────────────

class ImageGenerateRequest(BaseModel):
    prompt: str
    aspect_ratio: str = "9:16"
    reference_images: list[str] = []
    project_root: str = ""


class CharacterGenerateRequest(BaseModel):
    project_root: str
    characters: list[dict]  # [{name, prompt}]
    aspect_ratio: str = "9:16"


class SceneGenerateRequest(BaseModel):
    project_root: str
    scenes: list[dict]  # [{name, prompt, character_names}]
    aspect_ratio: str = "16:9"


# ── Helpers ─────────────────────────────────────────────────────

def _resolve_project_root(project_root: str) -> str:
    """Resolve project root from request or cwd walk."""
    if project_root and Path(project_root).is_dir():
        return str(Path(project_root).resolve())
    # Walk up from cwd
    cwd = Path.cwd()
    for _ in range(20):
        if (cwd / ".drama" / "state.json").exists():
            return str(cwd)
        if cwd.parent == cwd:
            break
        cwd = cwd.parent
    raise HTTPException(400, "Not in a drama project directory. Set project_root.")


# ── Routes ──────────────────────────────────────────────────────

@router.post("/image")
async def generate_image(req: ImageGenerateRequest):
    """Generate a single image. Optional reference_images for consistency."""
    refs = req.reference_images if req.reference_images else None
    result = await jimeng_provider.generate(req.prompt, req.aspect_ratio, reference_images=refs)
    return {
        "task_id": result.image_id,
        "status": "done",
        "image_url": result.image_url,
        "dimensions": result.dimensions,
    }


@router.post("/character")
async def generate_characters(req: CharacterGenerateRequest):
    """Generate character reference images. Auto-uploads to TOS and indexes."""
    project_root = _resolve_project_root(req.project_root)
    index = AssetIndex(project_root)
    results = []

    for char in req.characters:
        name = char["name"]
        prompt = char["prompt"]
        logger.info("Generating character: %s", name)

        result = await jimeng_provider.generate(prompt, req.aspect_ratio)
        image_url = result.image_url

        # If result is base64, upload to TOS for public URL
        tos_url = ""
        if image_url.startswith("data:"):
            header, b64 = image_url.split(",", 1)
            img_bytes = base64.b64decode(b64)
            tos_url = upload_to_tos(img_bytes, f"character/{name}")
        elif image_url.startswith("http"):
            tos_url = image_url

        # Save locally
        local_dir = Path(project_root) / "素材" / "角色"
        local_dir.mkdir(parents=True, exist_ok=True)
        local_path = str(local_dir / f"{name}.png")
        if image_url.startswith("data:"):
            with open(local_path, "wb") as f:
                f.write(base64.b64decode(image_url.split(",", 1)[1]))

        # Index
        index.add("character_image", name, tos_url=tos_url, local_path=local_path, prompt=prompt)

        results.append({
            "character": name,
            "status": "done",
            "tos_url": tos_url,
            "local_path": local_path,
        })

    return {"generated": results}


@router.post("/scene")
async def generate_scenes(req: SceneGenerateRequest):
    """Generate scene reference images with character references for consistency."""
    project_root = _resolve_project_root(req.project_root)
    index = AssetIndex(project_root)
    all_char_tos = index.get_all_characters()
    results = []

    for scene in req.scenes:
        name = scene["name"]
        prompt = scene["prompt"]
        char_names = scene.get("character_names", [])

        # Collect reference TOS URLs for characters in this scene
        refs = [all_char_tos[cn] for cn in char_names if cn in all_char_tos]
        logger.info("Generating scene: %s with %d character refs", name, len(refs))

        result = await jimeng_provider.generate(prompt, req.aspect_ratio, reference_images=refs if refs else None)
        image_url = result.image_url

        tos_url = ""
        if image_url.startswith("data:"):
            header, b64 = image_url.split(",", 1)
            img_bytes = base64.b64decode(b64)
            tos_url = upload_to_tos(img_bytes, f"scene/{name}")
        elif image_url.startswith("http"):
            tos_url = image_url

        local_dir = Path(project_root) / "素材" / "场景"
        local_dir.mkdir(parents=True, exist_ok=True)
        local_path = str(local_dir / f"{name}.png")
        if image_url.startswith("data:"):
            with open(local_path, "wb") as f:
                f.write(base64.b64decode(image_url.split(",", 1)[1]))

        index.add("scene_image", name, tos_url=tos_url, local_path=local_path, prompt=prompt)

        results.append({
            "scene": name,
            "status": "done",
            "tos_url": tos_url,
            "local_path": local_path,
            "character_refs_used": refs,
        })

    return {"generated": results}


@router.get("/assets")
async def list_assets(project_root: str = ""):
    """List all generated assets for a project."""
    project_root = _resolve_project_root(project_root)
    index = AssetIndex(project_root)
    return index.to_dict()


@router.get("/health")
async def health():
    return {"status": "ok", "provider": "jimeng46"}
