"""测试 video-cover CLI 命令。

video-cover 是新增命令，包装 jimeng.generate 生成单张图片作为视频封面。
"""
import asyncio
import base64
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# 让测试可以 import app
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.utils.asset_index import AssetIndex


def test_video_cover_writes_file_and_index(tmp_path, monkeypatch):
    """video-cover 应生成图片文件、写入 assets.json covers 段。"""
    # Arrange: 创建项目结构
    project = tmp_path / "my_video"
    project.mkdir()
    (project / ".drama").mkdir()
    AssetIndex(str(project))  # 初始化

    # Mock jimeng.generate 返回假图片
    fake_bytes = b"\x89PNG\r\n\x1a\n" + b"fakepngdata" * 10
    async def fake_generate(prompt, aspect_ratio, reference_images=None):
        result = MagicMock()
        result.image_url = "data:image/png;base64," + base64.b64encode(fake_bytes).decode()
        return result
    monkeypatch.setattr("app.cli.jimeng.generate", fake_generate)

    # Mock TOS 上传
    monkeypatch.setattr("app.cli.upload_to_tos", lambda b, t: "https://tos.example/cover.png")

    # Act: 调用 video-cover
    from app.cli import cmd_video_cover
    args = MagicMock()
    args.project = str(project)
    args.prompt = "一只可爱的猫咪作为视频封面"
    args.ratio = "9:16"
    args.name = "封面"

    asyncio.run(cmd_video_cover(args))

    # Assert: 文件存在
    cover_path = project / "素材" / "封面" / "封面.png"
    assert cover_path.exists(), f"封面文件未生成: {cover_path}"
    assert cover_path.read_bytes() == fake_bytes

    # Assert: assets.json 记录
    index = AssetIndex(str(project))
    covers = index.to_dict().get("covers", {})
    assert "封面" in covers, f"assets.json 未记录封面: {covers}"
    assert covers["封面"]["tos_url"] == "https://tos.example/cover.png"


def test_video_cover_skips_when_exists(tmp_path, monkeypatch, capsys):
    """video-cover 在文件已存在时跳过。"""
    project = tmp_path / "my_video"
    project.mkdir()
    (project / ".drama").mkdir()
    (project / "素材" / "封面").mkdir(parents=True)
    existing = project / "素材" / "封面" / "封面.png"
    existing.write_bytes(b"existing")

    from app.utils.asset_index import AssetIndex
    AssetIndex(str(project))

    # 不应调 jimeng
    async def fail_generate(*a, **kw):
        raise AssertionError("jimeng.generate 不应被调用")
    monkeypatch.setattr("app.cli.jimeng.generate", fail_generate)

    from app.cli import cmd_video_cover
    args = MagicMock()
    args.project = str(project)
    args.prompt = "..."
    args.ratio = "9:16"
    args.name = "封面"

    asyncio.run(cmd_video_cover(args))

    captured = capsys.readouterr()
    assert "已存在" in captured.out
    assert existing.read_bytes() == b"existing"
