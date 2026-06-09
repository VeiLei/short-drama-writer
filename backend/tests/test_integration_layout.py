"""End-to-end test: 模拟完整工作流，从 scene layout 到 layout-check。"""
import json
import os
import subprocess
import sys
import tempfile


def test_full_layout_check_workflow(tmp_path):
    """完整流程：录入 layout → 写视频提示词 → 跑 layout-check → 看到报告。"""
    project = tmp_path / "test_project"
    project.mkdir()
    (project / ".drama").mkdir()
    (project / "提示词").mkdir()

    # 1. Setup: write a scene layout via AssetIndex
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
    from app.utils.asset_index import AssetIndex

    idx = AssetIndex(str(project))
    layout = {
        "view": "front_elev",
        "fixed_objects": [
            {"id": "sofa_L", "name": "L型沙发", "position": "画面左下"},
            {"id": "tv_wall", "name": "电视墙", "position": "后景中央"},
        ],
        "walkable_zones": []
    }
    idx.add_scene_layout("客厅", layout)

    # 2. Write a video prompt JSON with intentional issues
    prompt_data = {
        "shots": [
            {
                "shot_id": "S1_F01",
                "scene_reference": {"scene_name": "客厅", "frame_id": "客厅_master"},
                "spatial_anchors": {"sofa_L": "画面左下", "tv_wall": "后景中央"}
            },
            {
                "shot_id": "S1_F02",
                "scene_reference": {"scene_name": "客厅", "frame_id": "客厅_master"},
                "spatial_anchors": {"sofa_L": "画面左下", "fake_door": "右侧"}
            },
            {
                "shot_id": "S1_F03",
                "scene_reference": {"scene_name": "客厅", "frame_id": "客厅_master"},
                "spatial_anchors": {"sofa_L": "画面左下"}
            }
        ]
    }
    with open(project / "提示词" / "第0001集-视频提示词.json", "w", encoding="utf-8") as f:
        json.dump(prompt_data, f, ensure_ascii=False)

    # 3. Run CLI layout-check
    backend_dir = os.path.join(os.path.dirname(__file__), "..")
    result = subprocess.run(
        [sys.executable, "-m", "app.cli", "layout-check",
         "--project", str(project), "--episode", "0001", "--skip-missing"],
        cwd=backend_dir,
        capture_output=True,
        text=True,
        encoding="utf-8",
        env={**os.environ, "PYTHONIOENCODING": "utf-8"},
    )

    # 4. Verify output
    assert "fake_door" in result.stdout, f"Should report fake_door as invalid: {result.stdout}"
    assert "invalid_key" in result.stdout, "Should categorize as invalid_key"
    assert result.returncode == 2, f"Should exit with blocking error code, got {result.returncode}"


def test_clean_passes(tmp_path):
    """干净数据应通过校验。"""
    project = tmp_path / "test_project"
    project.mkdir()
    (project / ".drama").mkdir()
    (project / "提示词").mkdir()

    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
    from app.utils.asset_index import AssetIndex

    idx = AssetIndex(str(project))
    idx.add_scene_layout("客厅", {
        "view": "front_elev",
        "fixed_objects": [{"id": "sofa_L", "name": "沙发", "position": "左下"}],
        "walkable_zones": []
    })

    prompt_data = {
        "shots": [
            {
                "shot_id": "S1_F01",
                "scene_reference": {"scene_name": "客厅", "frame_id": "客厅_master"},
                "spatial_anchors": {"sofa_L": "左下"}
            }
        ]
    }
    with open(project / "提示词" / "第0001集-视频提示词.json", "w", encoding="utf-8") as f:
        json.dump(prompt_data, f, ensure_ascii=False)

    backend_dir = os.path.join(os.path.dirname(__file__), "..")
    result = subprocess.run(
        [sys.executable, "-m", "app.cli", "layout-check",
         "--project", str(project), "--episode", "0001", "--skip-missing"],
        cwd=backend_dir,
        capture_output=True,
        text=True,
        encoding="utf-8",
        env={**os.environ, "PYTHONIOENCODING": "utf-8"},
    )

    assert "通过" in result.stdout or "无问题" in result.stdout
    assert result.returncode == 0
