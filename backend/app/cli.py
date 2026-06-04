"""Drama asset generation CLI.

Usage:
  python -m app.cli four-views  --project . --name <角色名> --prompt <prompt>
  python -m app.cli variant     --project . --name <角色名> --outfit <着装> --prompt <prompt>
  python -m app.cli scene-master --project . --name <场景名> --prompt <prompt>
  python -m app.cli shot-frame  --project . --scene <场景> --frame-id <id> --frame-type <type> --prompt <prompt>
  python -m app.cli assets      --project .

Prompt can be passed inline or read from a file / stdin:
  --prompt "text"
  --prompt @path/to/file.txt
  --prompt -   (reads from stdin)
  echo "prompt..." | python -m app.cli four-views --name X --prompt -
"""

import argparse
import asyncio
import base64
import logging
import sys
from pathlib import Path

from app.image_providers.jimeng46_adapter import jimeng
from app.utils.tos import upload_to_tos
from app.utils.asset_index import AssetIndex
from app.video_providers.seedance_adapter import seedance as video_provider

logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
logger = logging.getLogger("cli")


# ── Helpers ───────────────────────────────────────────────────────

def resolve_project(project_root: str) -> str:
    if project_root and Path(project_root).is_dir():
        return str(Path(project_root).resolve())
    cwd = Path.cwd()
    for _ in range(20):
        if (cwd / ".drama" / "state.json").exists():
            return str(cwd)
        if cwd.parent == cwd:
            break
        cwd = cwd.parent
    sys.exit("Error: Not in a drama project directory. Use --project to specify one.")


def read_prompt(value: str) -> str:
    if value == "-":
        return sys.stdin.read().strip()
    if value.startswith("@"):
        return Path(value[1:]).read_text(encoding="utf-8").strip()
    return value


async def gen_and_upload(prompt: str, aspect_ratio: str, refs: list[str] | None = None):
    result = await jimeng.generate(prompt, aspect_ratio, reference_images=refs or None)
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


# ── Commands ──────────────────────────────────────────────────────

async def cmd_four_views(args):
    project_root = resolve_project(args.project)
    prompt = read_prompt(args.prompt)
    index = AssetIndex(project_root)

    logger.info("Four-views: %s", args.name)
    image_url, tos_url, img_bytes = await gen_and_upload(prompt, args.ratio)

    local_dir = Path(project_root) / "素材" / "角色"
    local_dir.mkdir(parents=True, exist_ok=True)
    local_path = str(local_dir / f"{args.name}_基础.png")
    if img_bytes:
        local_path = str(local_dir / f"{args.name}_基础.png")
        with open(local_path, "wb") as f:
            f.write(img_bytes)

    index.add_character(args.name, tos_url=tos_url, local_path=local_path,
                        outfit="基础", is_base=True, prompt=prompt)
    print(f"✓ {args.name} 基础四视图 → {tos_url}")


async def cmd_variant(args):
    project_root = resolve_project(args.project)
    prompt = read_prompt(args.prompt)
    index = AssetIndex(project_root)

    base = index.get_character_base(args.name)
    if not base:
        sys.exit(f"Error: {args.name} 基础四视图不存在，先生成基础版")
    if index.character_has_outfit(args.name, args.outfit):
        print(f"⊙ {args.name}/{args.outfit} 已存在，跳过")
        return

    logger.info("Variant: %s / %s", args.name, args.outfit)
    refs = [base["tos_url"]] if base.get("tos_url") else None
    image_url, tos_url, img_bytes = await gen_and_upload(prompt, args.ratio, refs)

    local_dir = Path(project_root) / "素材" / "角色"
    local_dir.mkdir(parents=True, exist_ok=True)
    safe_outfit = args.outfit.replace("/", "_").replace(" ", "_")
    local_path = str(local_dir / f"{args.name}_{safe_outfit}.png")
    if img_bytes:
        with open(local_path, "wb") as f:
            f.write(img_bytes)

    index.add_character(args.name, tos_url=tos_url, local_path=local_path,
                        outfit=args.outfit, is_base=False, prompt=prompt)
    print(f"✓ {args.name}/{args.outfit} → {tos_url}")


async def cmd_scene_master(args):
    project_root = resolve_project(args.project)
    prompt = read_prompt(args.prompt)
    index = AssetIndex(project_root)

    existing = index.get_scene_master(args.name)
    if existing:
        print(f"⊙ {args.name} 全景图已存在，跳过 ({existing['tos_url']})")
        return

    logger.info("Scene master: %s", args.name)
    image_url, tos_url, img_bytes = await gen_and_upload(prompt, args.ratio)

    local_dir = Path(project_root) / "素材" / "场景"
    local_dir.mkdir(parents=True, exist_ok=True)
    local_path = str(local_dir / f"{args.name}_master.png")
    if img_bytes:
        with open(local_path, "wb") as f:
            f.write(img_bytes)

    index.add_scene_master(args.name, tos_url=tos_url, local_path=local_path, prompt=prompt)
    print(f"✓ {args.name} 全景图 → {tos_url}")


async def cmd_shot_frame(args):
    project_root = resolve_project(args.project)
    prompt = read_prompt(args.prompt)
    index = AssetIndex(project_root)

    if index.has_shot_frame(args.scene, args.frame_id):
        print(f"⊙ {args.scene}/{args.frame_id} 取景框已存在，跳过")
        return

    master = index.get_scene_master(args.scene)
    refs = [master["tos_url"]] if master and master.get("tos_url") else None

    logger.info("Shot frame: %s / %s (%s)", args.scene, args.frame_id, args.frame_type)
    image_url, tos_url, img_bytes = await gen_and_upload(prompt, args.ratio, refs)

    local_dir = Path(project_root) / "素材" / "场景"
    local_dir.mkdir(parents=True, exist_ok=True)
    local_path = str(local_dir / f"{args.scene}_{args.frame_id}.png")
    if img_bytes:
        with open(local_path, "wb") as f:
            f.write(img_bytes)

    index.add_shot_frame(args.scene, args.frame_id, args.frame_type,
                         tos_url=tos_url, local_path=local_path, prompt=prompt)
    print(f"✓ {args.scene}/{args.frame_id} → {tos_url}")


def cmd_assets(args):
    project_root = resolve_project(args.project)
    index = AssetIndex(project_root)
    data = index.to_dict()

    chars = data.get("characters", {})
    scenes = data.get("scenes", {})

    print(f"Project: {project_root}")
    print(f"Updated: {data.get('updated_at', 'N/A')}")
    print()

    print("── 角色 ──")
    if chars:
        for name, cdata in chars.items():
            variants = cdata.get("variants", [])
            outfits = [v.get("outfit", "?") for v in variants]
            print(f"  {name}  outfits: {', '.join(outfits)} ({len(variants)} variants)")
    else:
        print("  (空)")

    print()
    print("── 场景 ──")
    if scenes:
        for name, sdata in scenes.items():
            master = "✓" if sdata.get("master") else "✗"
            frames = sdata.get("shot_frames", [])
            frame_ids = [f.get("frame_id", "?") for f in frames]
            print(f"  {name}  master: {master}  frames: {', '.join(frame_ids) if frame_ids else '(空)'} ({len(frames)} frames)")
    else:
        print("  (空)")


async def cmd_video_generate(args):
    """生成视频：submit task 到 Seedance → poll 直到完成 → 下载到本地。"""
    import requests as req

    project_root = resolve_project(args.project)
    prompt = read_prompt(args.prompt)
    refs = [r.strip() for r in (args.refs or "").split(",") if r.strip()] if args.refs else None

    logger.info("Video generate: ratio=%s duration=%s", args.ratio, args.duration)
    result = await video_provider.generate(
        prompt, reference_images=refs, ratio=args.ratio, duration=args.duration,
    )

    video_dir = Path(project_root) / "素材" / "视频"
    video_dir.mkdir(parents=True, exist_ok=True)
    local_path = str(video_dir / f"{result.video_id}.mp4")

    if result.video_url:
        logger.info("Downloading video: %s", result.video_url[:80])
        r = req.get(result.video_url, timeout=300)
        r.raise_for_status()
        with open(local_path, "wb") as f:
            f.write(r.content)
        result.file_path = local_path
        print(f"✓ video → {local_path}  ({result.dimensions}, {result.duration}s)")
    else:
        print(f"✗ video failed: {result.api_response}")

    return result


def cmd_video_prompt(args):
    """显示或生成某个剧集的视频提示词 JSON。"""
    project_root = resolve_project(args.project)
    prompt_dir = Path(project_root) / "提示词"
    prompt_file = prompt_dir / f"第{args.episode}集-视频提示词.json"

    if prompt_file.exists():
        import json as _json
        data = _json.loads(prompt_file.read_text(encoding="utf-8"))
        shots = data.get("shots", [])
        print(f"Episode: {data.get('episode_id', 'N/A')}")
        print(f"Title:   {data.get('episode_title', 'N/A')}")
        print(f"Shots:   {len(shots)}")
        for s in shots[:5]:
            print(f"  {s.get('shot_id')}  {s.get('frame_type')}  dur={s.get('video_params', {}).get('duration_sec', '?')}s")
        if len(shots) > 5:
            print(f"  ... +{len(shots) - 5} more")
    else:
        print(f"(not found) {prompt_file}")
        print("Video prompts are generated during /drama-write. Run drama-write first.")


# ── Main ──────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Drama asset generation CLI")
    sub = parser.add_subparsers(dest="command")

    p = sub.add_parser("four-views", help="Generate character base four-views")
    p.add_argument("--project", required=True, help="Project directory path")
    p.add_argument("--name", required=True, help="Character name")
    p.add_argument("--prompt", required=True, help="Image prompt (use '-' for stdin, '@file' for file)")
    p.add_argument("--ratio", default="16:9", help="Aspect ratio (default: 16:9)")

    p = sub.add_parser("variant", help="Generate character outfit variant")
    p.add_argument("--project", required=True)
    p.add_argument("--name", required=True, help="Character name")
    p.add_argument("--outfit", required=True, help="Outfit name")
    p.add_argument("--prompt", required=True, help="Image prompt (use '-' for stdin, '@file' for file)")
    p.add_argument("--ratio", default="16:9", help="Aspect ratio (default: 16:9)")

    p = sub.add_parser("scene-master", help="Generate scene panoramic master")
    p.add_argument("--project", required=True)
    p.add_argument("--name", required=True, help="Scene name")
    p.add_argument("--prompt", required=True, help="Image prompt (use '-' for stdin, '@file' for file)")
    p.add_argument("--ratio", default="9:16", help="Aspect ratio (default: 9:16)")

    p = sub.add_parser("shot-frame", help="Generate scene shot frame")
    p.add_argument("--project", required=True)
    p.add_argument("--scene", required=True, help="Scene name")
    p.add_argument("--frame-id", required=True, help="Frame identifier")
    p.add_argument("--frame-type", required=True, help="Frame type (e.g. two_shot, establishing)")
    p.add_argument("--prompt", required=True, help="Image prompt (use '-' for stdin, '@file' for file)")
    p.add_argument("--ratio", default="9:16", help="Aspect ratio (default: 9:16)")

    p = sub.add_parser("assets", help="List all generated assets")
    p.add_argument("--project", required=True, help="Project directory path")

    p = sub.add_parser("video-generate", help="Generate video via Seedance")
    p.add_argument("--project", required=True, help="Project directory path")
    p.add_argument("--prompt", required=True, help="Video prompt (use '-' for stdin, '@file' for file)")
    p.add_argument("--ratio", default="9:16", help="Aspect ratio (default: 9:16)")
    p.add_argument("--duration", type=int, default=10, help="Video duration in seconds (default: 10)")
    p.add_argument("--refs", default=None, help="Comma-separated reference image URLs")

    p = sub.add_parser("video-prompt", help="Show video prompt JSON for an episode")
    p.add_argument("--project", required=True, help="Project directory path")
    p.add_argument("--episode", required=True, help="Episode ID (e.g. 0001)")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    sync_cmds = {"assets", "video-prompt"}
    if args.command in sync_cmds:
        globals()[f"cmd_{args.command.replace('-', '_')}"](args)
    else:
        asyncio.run(globals()[f"cmd_{args.command.replace('-', '_')}"](args))


if __name__ == "__main__":
    main()
