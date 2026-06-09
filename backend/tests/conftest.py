import os
import sys
import tempfile
import pytest

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


@pytest.fixture
def tmp_project(tmp_path):
    """Create a temporary project root with .drama directory."""
    (tmp_path / ".drama").mkdir()
    return str(tmp_path)


@pytest.fixture
def sample_scene_layout():
    return {
        "view": "front_elev",
        "description": "客厅正面视角",
        "fixed_objects": [
            {"id": "sofa_L", "name": "L型沙发", "position": "画面左下区域",
             "size": "占画面横向1/3", "orientation": "开口朝右"},
            {"id": "tv_wall", "name": "电视墙", "position": "画面后景中央",
             "size": "占画面横向1/4", "orientation": "正面朝镜头"},
            {"id": "window_R", "name": "落地窗", "position": "画面右侧通顶",
             "size": "占画面右侧1/3", "orientation": "朝内"},
        ],
        "walkable_zones": [
            {"id": "center_floor", "position": "画面中央中景",
             "description": "沙发与电视之间的活动区"}
        ]
    }
