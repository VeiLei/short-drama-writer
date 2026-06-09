"""Drama asset generation CLI.

Usage:
  python -m app.cli four-views   --project . --name <角色名> --prompt <prompt>
  python -m app.cli variant      --project . --name <角色名> --outfit <着装> --prompt <prompt>
  python -m app.cli scene-master --project . --name <场景名> --prompt <prompt>
  python -m app.cli shot-frame   --project . --scene <场景> --frame-id <id> --frame-type <type> --prompt <prompt>
  python -m app.cli prop-ref     --project . --name <道具名> --prompt <prompt>
  python -m app.cli assets       --project .

Prompt can be passed inline or read from a file / stdin:
  --prompt "text"
  --prompt @path/to/file.txt
  --prompt -   (reads from stdin)
  echo "prompt..." | python -m app.cli four-views --name X --prompt -
"""

import argparse
import asyncio
import base64
import json
import logging
import sys
from pathlib import Path

from app.image_providers.jimeng46_adapter import jimeng
from app.utils.tos import upload_to_tos
from app.utils.asset_index import AssetIndex
from app.video_providers.seedance_adapter import seedance as video_provider

# Force UTF-8 stdout to avoid GBK print errors on Windows
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

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

    layout = None
    if args.layout:
        layout = _parse_layout_arg(args.layout)
        if layout is None:
            sys.exit(f"Error: --layout 解析失败，参看 help")

    logger.info("Scene master: %s (layout=%s)", args.name, "yes" if layout else "no")
    image_url, tos_url, img_bytes = await gen_and_upload(prompt, args.ratio)

    local_dir = Path(project_root) / "素材" / "场景"
    local_dir.mkdir(parents=True, exist_ok=True)
    local_path = str(local_dir / f"{args.name}_master.png")
    if img_bytes:
        with open(local_path, "wb") as f:
            f.write(img_bytes)

    index.add_scene_master(args.name, tos_url=tos_url, local_path=local_path,
                           prompt=prompt, layout=layout)
    if layout:
        print(f"✓ {args.name} 全景图 + spatial_layout ({len(layout.get('fixed_objects', []))} 固定物) → {tos_url}")
    else:
        print(f"✓ {args.name} 全景图 → {tos_url}")


def _parse_layout_arg(value: str) -> Optional[dict]:
    """解析 --layout 参数：支持 @file.json 路径或内联 JSON 字符串。"""
    try:
        if value.startswith("@"):
            return json.loads(Path(value[1:]).read_text(encoding="utf-8"))
        return json.loads(value)
    except (json.JSONDecodeError, OSError) as e:
        print(f"Error: --layout 解析失败: {e}", file=sys.stderr)
        return None


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


async def cmd_prop_ref(args):
    project_root = resolve_project(args.project)
    prompt = read_prompt(args.prompt)
    index = AssetIndex(project_root)

    if index.prop_exists(args.name):
        print(f"⊙ 道具 {args.name} 参考图已存在，跳过")
        return

    logger.info("Prop ref: %s", args.name)
    image_url, tos_url, img_bytes = await gen_and_upload(prompt, args.ratio)

    local_dir = Path(project_root) / "素材" / "道具"
    local_dir.mkdir(parents=True, exist_ok=True)
    safe_name = args.name.replace("/", "_").replace(" ", "_")
    local_path = str(local_dir / f"{safe_name}.png")
    if img_bytes:
        with open(local_path, "wb") as f:
            f.write(img_bytes)

    index.add_prop(args.name, tos_url=tos_url, local_path=local_path,
                   scene_name=args.scene or "", prompt=prompt)
    print(f"✓ 道具 {args.name} → {tos_url}")


def cmd_assets(args):
    project_root = resolve_project(args.project)
    index = AssetIndex(project_root)
    data = index.to_dict()

    chars = data.get("characters", {})
    scenes = data.get("scenes", {})
    props = data.get("props", {})

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

    print()
    print("── 道具 ──")
    if props:
        for name, pdata in props.items():
            scene = pdata.get("scene_name", "")
            scene_tag = f" [{scene}]" if scene else ""
            print(f"  {name}{scene_tag} → {pdata.get('tos_url', '?')[:60]}")
    else:
        print("  (空)")


async def cmd_video_generate(args):
    """生成视频：submit task 到 Seedance → poll 直到完成 → 下载到本地。"""
    import requests as req

    project_root = resolve_project(args.project)
    index = AssetIndex(project_root)

    # Resolve prompt and refs
    if args.episode and args.shot_id:
        # Auto-lookup from video prompt JSON + assets.json
        prompt_dir = Path(project_root) / "提示词"
        prompt_file = prompt_dir / f"第{args.episode}集-视频提示词.json"
        if not prompt_file.exists():
            sys.exit(f"Video prompt JSON not found: {prompt_file}")
        data = json.loads(prompt_file.read_text(encoding="utf-8"))
        shot = next((s for s in data.get("shots", []) if s.get("shot_id") == args.shot_id), None)
        if not shot:
            sys.exit(f"Shot {args.shot_id} not found in episode {args.episode}")
        shot_prompt = shot["prompt"]
        video_params = shot.get("video_params", {})

        # Build prompt text
        prompt = shot_prompt.get("positive", read_prompt(args.prompt or ""))

        # ── Resolve scene ref ──
        scene_url = ""
        if args.scene:
            if args.frame_id:
                scene_url = index.get_shot_frame_url(args.scene, args.frame_id)
            else:
                scene_url = index.get_scene_master_url(args.scene)
            if scene_url:
                logger.info("  scene ref: %s/%s → %s", args.scene, args.frame_id or "master", scene_url[:80])
            else:
                logger.warning("  scene not found: %s/%s", args.scene, args.frame_id or "master")

        # ── Resolve character refs ──
        char_refs = shot_prompt.get("character_references", [])
        char_urls = []
        char_names = []
        for cr in char_refs:
            clean_name = cr.get("name", "").split("（")[0].split("(")[0].strip()
            clean_outfit = cr.get("outfit", "基础").split("，")[0].split(",")[0].strip()
            tos = index.get_character_tos_url(clean_name, clean_outfit)
            if tos:
                char_urls.append(tos)
                char_names.append(clean_name)
                logger.info("  matched character: %s/%s → %s", clean_name, clean_outfit, tos[:80])
            else:
                logger.warning("  character not found: %s/%s", clean_name, clean_outfit)

        # ── Resolve prop refs ──
        prop_refs = shot_prompt.get("prop_references", [])
        prop_urls = []
        prop_names = []
        for pr in prop_refs:
            prop_name = pr if isinstance(pr, str) else pr.get("name", "")
            tos = index.get_prop_tos_url(prop_name)
            if tos:
                prop_urls.append(tos)
                prop_names.append(prop_name)
                logger.info("  matched prop: %s → %s", prop_name, tos[:80])
            else:
                logger.warning("  prop not found: %s", prop_name)

        # ── Build ref_urls: scene → characters → props ──
        ref_urls = (scene_url and [scene_url] or []) + char_urls + prop_urls
        img_idx = 0
        ref_parts = []

        if scene_url:
            img_idx += 1
            ref_parts.append(f"参考图{img_idx}是场景空镜，场景环境以参考图{img_idx}为准")

        for i, name in enumerate(char_names):
            img_idx += 1
            ref_parts.append(f"参考图{img_idx}是角色立绘（{name}），角色外貌以参考图为基准")

        for i, name in enumerate(prop_names):
            img_idx += 1
            ref_parts.append(f"参考图{img_idx}是道具参考图（{name}），道具造型以参考图为基准")

        if ref_parts:
            prompt = "。".join(ref_parts) + "。" + prompt

        # ── Narration mode: prepend style prefix ──
        if getattr(args, "mode", None) == "narration":
            narration_prefix = (
                "镜头以自然讲述的视角展开，人物口型与节奏与旁白同步，"
                "画面有适度的镜头呼吸感与场景氛围，环境音清晰。"
            )
            prompt = narration_prefix + prompt
            logger.info("  mode=narration: prefix injected")

        if not args.ratio:
            args.ratio = video_params.get("aspect_ratio", "9:16")
        if not args.duration:
            args.duration = video_params.get("duration_sec", 10)
    else:
        prompt = read_prompt(args.prompt)
        ref_urls = [r.strip() for r in (args.refs or "").split(",") if r.strip()] if args.refs else None
        if args.duration is None:
            args.duration = 10

    logger.info("Video generate: ratio=%s duration=%s refs=%d", args.ratio, args.duration,
                len(ref_urls) if ref_urls else 0)
    result = await video_provider.generate(
        prompt, reference_images=ref_urls or None, ratio=args.ratio, duration=args.duration,
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


async def cmd_video_cover(args):
    """生成视频封面。包装 jimeng.generate，写入 assets.json covers 段。"""
    project_root = resolve_project(args.project)
    prompt = read_prompt(args.prompt)
    index = AssetIndex(project_root)

    # 幂等：已存在则跳过
    local_dir = Path(project_root) / "素材" / "封面"
    local_dir.mkdir(parents=True, exist_ok=True)
    local_path = local_dir / f"{args.name}.png"
    if local_path.exists():
        print(f"⊙ {args.name} 封面已存在，跳过")
        return

    logger.info("Video cover: %s", args.name)
    image_url, tos_url, img_bytes = await gen_and_upload(prompt, args.ratio)

    if img_bytes:
        with open(local_path, "wb") as f:
            f.write(img_bytes)

    index.add_cover(args.name, tos_url=tos_url, local_path=str(local_path), prompt=prompt)
    print(f"✓ {args.name} 封面 → {tos_url}")


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
    p.add_argument("--layout", default=None, help="Scene spatial layout JSON (inline or '@file.json')")

    p = sub.add_parser("shot-frame", help="Generate scene shot frame")
    p.add_argument("--project", required=True)
    p.add_argument("--scene", required=True, help="Scene name")
    p.add_argument("--frame-id", required=True, help="Frame identifier")
    p.add_argument("--frame-type", required=True, help="Frame type (e.g. two_shot, establishing)")
    p.add_argument("--prompt", required=True, help="Image prompt (use '-' for stdin, '@file' for file)")
    p.add_argument("--ratio", default="9:16", help="Aspect ratio (default: 9:16)")

    p = sub.add_parser("prop-ref", help="Generate prop reference image")
    p.add_argument("--project", required=True)
    p.add_argument("--name", required=True, help="Prop name")
    p.add_argument("--prompt", required=True, help="Image prompt (use '-' for stdin, '@file' for file)")
    p.add_argument("--ratio", default="1:1", help="Aspect ratio (default: 1:1)")
    p.add_argument("--scene", default=None, help="Associated scene name (optional)")

    p = sub.add_parser("assets", help="List all generated assets")
    p.add_argument("--project", required=True, help="Project directory path")

    p = sub.add_parser("video-cover", help="Generate video cover image (wraps jimeng.generate)")
    p.add_argument("--project", required=True, help="Project directory path")
    p.add_argument("--name", required=True, help="Cover name (e.g., '封面' or 'cover_v1')")
    p.add_argument("--prompt", required=True, help="Image prompt (use '-' for stdin, '@file' for file)")
    p.add_argument("--ratio", default="9:16", help="Aspect ratio (default: 9:16)")

    p = sub.add_parser("video-generate", help="Generate video via Seedance")
    p.add_argument("--project", required=True, help="Project directory path")
    p.add_argument("--prompt", default="", help="Video prompt (use '-' for stdin, '@file' for file)")
    p.add_argument("--ratio", default="9:16", help="Aspect ratio (default: 9:16)")
    p.add_argument("--duration", type=int, default=None, help="Video duration in seconds (default: read from video_params.duration_sec, fallback 10)")
    p.add_argument("--refs", default=None, help="Comma-separated reference image URLs")
    # Auto-lookup mode: read from video prompt JSON + assets.json
    p.add_argument("--episode", default=None, help="Episode ID (e.g. 0001) — auto-resolve prompt+refs")
    p.add_argument("--shot-id", default=None, help="Shot ID (e.g. S1_F01) — used with --episode")
    p.add_argument("--scene", default=None, help="Scene name for auto scene ref lookup")
    p.add_argument("--frame-id", default=None, help="Shot frame ID for auto scene ref lookup")
    p.add_argument("--mode", default=None, choices=[None, "narration"],
                   help="Generation mode: 'narration' injects narrator-style prefix into prompt")

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
