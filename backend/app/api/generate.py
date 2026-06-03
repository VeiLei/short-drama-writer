"""Asset generation API routes.

角色：基础四视图 (four_views) + 变装四视图 (variant)
场景：全景参考图 (master) + 按需取景框 (shot_frame)
"""

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


# ── Helpers ─────────────────────────────────────────────────────

def _resolve_project(project_root: str) -> str:
    if project_root and Path(project_root).is_dir():
        return str(Path(project_root).resolve())
    cwd = Path.cwd()
    for _ in range(20):
        if (cwd / ".drama" / "state.json").exists():
            return str(cwd)
        if cwd.parent == cwd:
            break
        cwd = cwd.parent
    raise HTTPException(400, "Not in a drama project directory.")


async def _gen_and_upload(prompt: str, aspect_ratio: str, refs: list[str] = None):
    """生成图片 → 返回(image_url, tos_url, local_bytes)"""
    result = await jimeng_provider.generate(prompt, aspect_ratio, reference_images=refs or None)
    image_url = result.image_url

    tos_url = ""
    img_bytes = None
    if image_url.startswith("data:"):
        _, b64 = image_url.split(",", 1)
        img_bytes = base64.b64decode(b64)
        tos_url = upload_to_tos(img_bytes, "drama")
    elif image_url.startswith("http"):
        tos_url = image_url

    return image_url, tos_url, img_bytes


# ── Request models ───────────────────────────────────────────────

class FourViewsRequest(BaseModel):
    project_root: str
    characters: list[dict]  # [{name, prompt}]


class VariantRequest(BaseModel):
    project_root: str
    characters: list[dict]  # [{name, outfit, prompt}]


class SceneMasterRequest(BaseModel):
    project_root: str
    scenes: list[dict]  # [{name, prompt}]


class ShotFrameRequest(BaseModel):
    project_root: str
    frames: list[dict]  # [{scene_name, frame_id, frame_type, prompt}]


# ── 角色 ─────────────────────────────────────────────────────────

@router.post("/character/four-views")
async def generate_four_views(req: FourViewsRequest):
    """生成角色基础四视图。CG风格，16:9，白底，空镜无背景。"""
    project_root = _resolve_project(req.project_root)
    index = AssetIndex(project_root)
    results = []

    for char in req.characters:
        name = char["name"]
        prompt = char["prompt"]
        logger.info("[FourViews] %s", name)

        image_url, tos_url, img_bytes = await _gen_and_upload(prompt, "16:9")
        local_dir = Path(project_root) / "素材" / "角色"
        local_dir.mkdir(parents=True, exist_ok=True)
        local_path = str(local_dir / f"{name}_基础.png")
        if img_bytes:
            local_dir.mkdir(parents=True, exist_ok=True)
            with open(local_path, "wb") as f:
                f.write(img_bytes)

        index.add_character(name, tos_url=tos_url, local_path=local_path,
                            outfit="基础", is_base=True, prompt=prompt)
        results.append({"character": name, "outfit": "基础", "tos_url": tos_url})

    return {"generated": results}


@router.post("/character/variant")
async def generate_variant(req: VariantRequest):
    """生成角色变装四视图。以基础四视图为 reference_image。"""
    project_root = _resolve_project(req.project_root)
    index = AssetIndex(project_root)
    results = []

    for char in req.characters:
        name = char["name"]
        outfit = char["outfit"]
        prompt = char["prompt"]

        base = index.get_character_base(name)
        if not base:
            results.append({"character": name, "outfit": outfit, "error": "基础四视图不存在，先生成基础版"})
            continue
        if index.character_has_outfit(name, outfit):
            results.append({"character": name, "outfit": outfit, "status": "已存在，跳过"})
            continue

        logger.info("[Variant] %s / %s", name, outfit)
        refs = [base["tos_url"]] if base.get("tos_url") else None
        image_url, tos_url, img_bytes = await _gen_and_upload(prompt, "16:9", refs)

        local_dir = Path(project_root) / "素材" / "角色"
        local_dir.mkdir(parents=True, exist_ok=True)
        safe_outfit = outfit.replace("/", "_").replace(" ", "_")
        local_path = str(local_dir / f"{name}_{safe_outfit}.png")
        if img_bytes:
            with open(local_path, "wb") as f:
                f.write(img_bytes)

        index.add_character(name, tos_url=tos_url, local_path=local_path,
                            outfit=outfit, is_base=False, prompt=prompt)
        results.append({"character": name, "outfit": outfit, "tos_url": tos_url})

    return {"generated": results}


# ── 场景 ─────────────────────────────────────────────────────────

@router.post("/scene/master")
async def generate_scene_master(req: SceneMasterRequest):
    """生成场景全景参考图。16:9空镜。"""
    project_root = _resolve_project(req.project_root)
    index = AssetIndex(project_root)
    results = []

    for scene in req.scenes:
        name = scene["name"]
        prompt = scene["prompt"]

        existing = index.get_scene_master(name)
        if existing:
            results.append({"scene": name, "status": "已存在", "tos_url": existing["tos_url"]})
            continue

        logger.info("[SceneMaster] %s", name)
        image_url, tos_url, img_bytes = await _gen_and_upload(prompt, "16:9")
        local_dir = Path(project_root) / "素材" / "场景"
        local_dir.mkdir(parents=True, exist_ok=True)
        local_path = str(local_dir / f"{name}_master.png")
        if img_bytes:
            with open(local_path, "wb") as f:
                f.write(img_bytes)

        index.add_scene_master(name, tos_url=tos_url, local_path=local_path, prompt=prompt)
        results.append({"scene": name, "tos_url": tos_url})

    return {"generated": results}


@router.post("/scene/shot-frame")
async def generate_shot_frame(req: ShotFrameRequest):
    """生成场景取景框。以场景全景图 (master) 为 reference_image 保证一致性。空镜无人物。"""
    project_root = _resolve_project(req.project_root)
    index = AssetIndex(project_root)
    results = []

    for frame in req.frames:
        scene_name = frame["scene_name"]
        frame_id = frame["frame_id"]
        frame_type = frame["frame_type"]
        prompt = frame["prompt"]

        if index.has_shot_frame(scene_name, frame_id):
            results.append({"scene": scene_name, "frame_id": frame_id, "status": "已存在"})
            continue

        master = index.get_scene_master(scene_name)
        refs = [master["tos_url"]] if master and master.get("tos_url") else None

        logger.info("[ShotFrame] %s/%s", scene_name, frame_id)
        image_url, tos_url, img_bytes = await _gen_and_upload(prompt, "16:9", refs)

        local_dir = Path(project_root) / "素材" / "场景"
        local_dir.mkdir(parents=True, exist_ok=True)
        local_path = str(local_dir / f"{scene_name}_{frame_id}.png")
        if img_bytes:
            with open(local_path, "wb") as f:
                f.write(img_bytes)

        index.add_shot_frame(scene_name, frame_id, frame_type,
                             tos_url=tos_url, local_path=local_path, prompt=prompt)
        results.append({"scene": scene_name, "frame_id": frame_id, "tos_url": tos_url})

    return {"generated": results}


# ── 查询 ─────────────────────────────────────────────────────────

@router.get("/assets")
async def list_assets(project_root: str = ""):
    project_root = _resolve_project(project_root)
    return AssetIndex(project_root).to_dict()


@router.get("/health")
async def health():
    return {"status": "ok", "provider": "jimeng46"}
