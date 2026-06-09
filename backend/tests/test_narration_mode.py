"""测试 video-generate 的 --mode narration 标志。

当 --mode narration 传入时，prompt 应自动添加旁白前缀。
"""
import asyncio
import sys
from pathlib import Path
from unittest.mock import MagicMock

sys.path.insert(0, str(Path(__file__).parent.parent))


def test_narration_mode_prepends_prefix(tmp_path, monkeypatch):
    """--mode narration 会在 prompt 前添加旁白风格前缀。"""
    project = tmp_path / "my_video"
    project.mkdir()
    (project / ".drama").mkdir()

    captured_prompts = []

    # Mock video_provider.generate 捕获入参
    class FakeResult:
        video_id = "v_001"
        video_url = ""
        file_path = None
        duration = 0
        dimensions = ""
        aspect_ratio = "9:16"
        api_response = {}

    async def fake_generate(prompt, reference_images=None, ratio="9:16", duration=10, **kw):
        captured_prompts.append(prompt)
        return FakeResult()

    monkeypatch.setattr("app.cli.video_provider.generate", fake_generate)

    # Mock video prompt JSON 读取
    import json
    prompt_dir = project / "提示词"
    prompt_dir.mkdir()
    (prompt_dir / "第0001集-视频提示词.json").write_text(json.dumps({
        "episode_id": "0001",
        "shots": [
            {
                "shot_id": "S01",
                "prompt": {"positive": "小明在实验室里认真做实验"},
                "video_params": {"duration_sec": 6, "aspect_ratio": "9:16"},
                "character_references": [],
                "prop_references": [],
            }
        ]
    }), encoding="utf-8")

    from app.cli import cmd_video_generate
    args = MagicMock()
    args.project = str(project)
    args.episode = "0001"
    args.shot_id = "S01"
    args.scene = ""
    args.frame_id = ""
    args.prompt = ""
    args.ratio = ""
    args.duration = None
    args.refs = None
    args.mode = "narration"  # 新增标志

    asyncio.run(cmd_video_generate(args))

    assert len(captured_prompts) == 1
    p = captured_prompts[0]
    assert "自然讲述" in p or "narrator" in p.lower() or "视角" in p, \
        f"narration 模式未注入前缀。Got: {p[:200]}"
    assert "小明在实验室里认真做实验" in p, "原始 prompt 应保留"


def test_default_mode_unchanged(tmp_path, monkeypatch):
    """不传 --mode 时，prompt 不变。"""
    project = tmp_path / "my_video"
    project.mkdir()
    (project / ".drama").mkdir()

    captured_prompts = []

    class FakeResult:
        video_id = "v_002"
        video_url = ""
        file_path = None
        duration = 0
        dimensions = ""
        aspect_ratio = "9:16"
        api_response = {}

    async def fake_generate(prompt, **kw):
        captured_prompts.append(prompt)
        return FakeResult()

    monkeypatch.setattr("app.cli.video_provider.generate", fake_generate)

    import json
    prompt_dir = project / "提示词"
    prompt_dir.mkdir()
    (prompt_dir / "第0001集-视频提示词.json").write_text(json.dumps({
        "episode_id": "0001",
        "shots": [
            {
                "shot_id": "S01",
                "prompt": {"positive": "原始 prompt 不变"},
                "video_params": {"duration_sec": 6, "aspect_ratio": "9:16"},
                "character_references": [],
                "prop_references": [],
            }
        ]
    }), encoding="utf-8")

    from app.cli import cmd_video_generate
    args = MagicMock()
    args.project = str(project)
    args.episode = "0001"
    args.shot_id = "S01"
    args.scene = ""
    args.frame_id = ""
    args.prompt = ""
    args.ratio = ""
    args.duration = None
    args.refs = None
    args.mode = None  # 默认

    asyncio.run(cmd_video_generate(args))

    assert len(captured_prompts) == 1
    p = captured_prompts[0]
    # 默认模式不应注入 narration 前缀
    assert "自然讲述" not in p
    assert "原始 prompt 不变" in p
