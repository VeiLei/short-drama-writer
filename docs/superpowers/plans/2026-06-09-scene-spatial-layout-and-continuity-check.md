# Scene Spatial Layout & Continuity Check — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace AI-impersonated ASCII layouts with structured `spatial_layout` data captured at scene asset generation time, then validate cross-shot position continuity before video generation.

**Architecture:** Three layers: (1) `AssetIndex` extends JSON storage with `spatial_layout` and validation methods; (2) `cli.py` adds `--layout` parameters to scene commands and a new `layout-check` subcommand; (3) Plugin templates and skills enforce structured spatial writing at every stage. Validation runs offline against the video-prompt JSON, outputs AI-proposed diffs, human reviews, then writes back.

**Tech Stack:** Python 3.11, pytest, FastAPI backend, JSON file storage, no DB schema changes.

---

## File Structure

| File | Responsibility |
|------|----------------|
| `backend/app/utils/asset_index.py` | Add `add_scene_layout` / `get_scene_layout` / `get_fixed_object_ids` / `validate_spatial_anchors` / `get_check_report` methods |
| `backend/app/utils/layout_checker.py` (new) | Pure functions: `check_continuity(shots, layout) -> Report` |
| `backend/app/cli.py` | Add `--layout` / `--fixed-objects` params to scene commands; new `cmd_layout_check` subcommand |
| `backend/tests/test_asset_index.py` (new) | Test new methods |
| `backend/tests/test_layout_checker.py` (new) | Test continuity validation logic |
| `plugin/templates/scene-card.md` | Add "固定物空间布局" table |
| `plugin/templates/episode-script.md` | Remove ASCII layout, add reference pointer |
| `plugin/skills/drama-init/SKILL.md` | Document scene-card layout step |
| `plugin/skills/drama-generate/SKILL.md` | Update prompt templates to structured spatial format |
| `plugin/references/video-prompt-rules.md` | Add §3.2 spatial_anchors source constraint |

---

## Task 1: Test infrastructure setup

**Files:**
- Create: `backend/tests/__init__.py`
- Create: `backend/tests/conftest.py`
- Create: `backend/pytest.ini`

- [ ] **Step 1: Create test package init**

Create `backend/tests/__init__.py`:
```python
```

(empty file)

- [ ] **Step 2: Create pytest config**

Create `backend/pytest.ini`:
```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short
```

- [ ] **Step 3: Create conftest with sample fixtures**

Create `backend/tests/conftest.py`:
```python
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
```

- [ ] **Step 4: Verify pytest discovers tests**

Run: `cd backend && .venv/Scripts/python -m pytest --collect-only`
Expected: "no tests ran" (empty collection), exit code 5. This is correct since no tests exist yet.

- [ ] **Step 5: Commit**

```bash
git add backend/tests backend/pytest.ini
git commit -m "test: add pytest infrastructure"
```

---

## Task 2: AssetIndex — add_scene_layout + get_scene_layout

**Files:**
- Modify: `backend/app/utils/asset_index.py:81-105`
- Test: `backend/tests/test_asset_index.py`

- [ ] **Step 1: Write failing test**

Create `backend/tests/test_asset_index.py`:
```python
import json
from app.utils.asset_index import AssetIndex


def test_add_scene_layout_creates_new_scene(tmp_project, sample_scene_layout):
    idx = AssetIndex(tmp_project)
    idx.add_scene_layout("客厅", sample_scene_layout)

    stored = idx.get_scene_layout("客厅")
    assert stored == sample_scene_layout


def test_add_scene_layout_replaces_existing(tmp_project, sample_scene_layout):
    idx = AssetIndex(tmp_project)
    idx.add_scene_layout("客厅", sample_scene_layout)

    updated = dict(sample_scene_layout)
    updated["description"] = "updated description"
    idx.add_scene_layout("客厅", updated)

    assert idx.get_scene_layout("客厅")["description"] == "updated description"


def test_get_scene_layout_returns_none_for_missing(tmp_project):
    idx = AssetIndex(tmp_project)
    assert idx.get_scene_layout("不存在的场景") is None
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend && .venv/Scripts/python -m pytest tests/test_asset_index.py -v`
Expected: FAIL with `AttributeError: 'AssetIndex' object has no attribute 'add_scene_layout'`

- [ ] **Step 3: Implement add_scene_layout and get_scene_layout**

In `backend/app/utils/asset_index.py`, add new methods in the 场景 section (after line 105 `get_scene_master_url`):

```python
    def add_scene_layout(self, name: str, layout: dict) -> str:
        """添加/替换场景的固定物空间布局。"""
        data = self._read()
        scenes = data.setdefault("scenes", {})
        scene_entry = scenes.setdefault(name, {"master": None, "shot_frames": []})
        scene_entry["spatial_layout"] = layout
        self._write(data)
        return f"{name}/layout"

    def get_scene_layout(self, name: str) -> Optional[dict]:
        data = self._read()
        scene = data.get("scenes", {}).get(name, {})
        return scene.get("spatial_layout")
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd backend && .venv/Scripts/python -m pytest tests/test_asset_index.py -v`
Expected: PASS for all 3 tests

- [ ] **Step 5: Commit**

```bash
git add backend/app/utils/asset_index.py backend/tests/test_asset_index.py
git commit -m "feat(asset_index): add add_scene_layout and get_scene_layout"
```

---

## Task 3: AssetIndex — get_fixed_object_ids

**Files:**
- Modify: `backend/app/utils/asset_index.py`
- Test: `backend/tests/test_asset_index.py`

- [ ] **Step 1: Write failing test**

Append to `backend/tests/test_asset_index.py`:
```python
def test_get_fixed_object_ids_returns_all_ids(tmp_project, sample_scene_layout):
    idx = AssetIndex(tmp_project)
    idx.add_scene_layout("客厅", sample_scene_layout)

    ids = idx.get_fixed_object_ids("客厅")
    assert set(ids) == {"sofa_L", "tv_wall", "window_R", "center_floor"}


def test_get_fixed_object_ids_empty_when_no_layout(tmp_project):
    idx = AssetIndex(tmp_project)
    assert idx.get_fixed_object_ids("客厅") == []


def test_get_fixed_object_ids_missing_scene(tmp_project):
    idx = AssetIndex(tmp_project)
    assert idx.get_fixed_object_ids("不存在的场景") == []
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend && .venv/Scripts/python -m pytest tests/test_asset_index.py::test_get_fixed_object_ids_returns_all_ids -v`
Expected: FAIL with `AttributeError: 'AssetIndex' object has no attribute 'get_fixed_object_ids'`

- [ ] **Step 3: Implement get_fixed_object_ids**

Add after `get_scene_layout`:
```python
    def get_fixed_object_ids(self, name: str) -> list[str]:
        """列出场景 spatial_layout 中所有 fixed_objects 和 walkable_zones 的 id。"""
        layout = self.get_scene_layout(name)
        if not layout:
            return []
        ids = [obj["id"] for obj in layout.get("fixed_objects", []) if "id" in obj]
        ids += [zone["id"] for zone in layout.get("walkable_zones", []) if "id" in zone]
        return ids
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd backend && .venv/Scripts/python -m pytest tests/test_asset_index.py -v`
Expected: PASS for all 6 tests

- [ ] **Step 5: Commit**

```bash
git add backend/app/utils/asset_index.py backend/tests/test_asset_index.py
git commit -m "feat(asset_index): add get_fixed_object_ids"
```

---

## Task 4: AssetIndex — validate_spatial_anchors

**Files:**
- Modify: `backend/app/utils/asset_index.py`
- Test: `backend/tests/test_asset_index.py`

- [ ] **Step 1: Write failing test**

Append to `backend/tests/test_asset_index.py`:
```python
def test_validate_spatial_anchors_all_valid(tmp_project, sample_scene_layout):
    idx = AssetIndex(tmp_project)
    idx.add_scene_layout("客厅", sample_scene_layout)

    anchors = {"sofa_L": "画面左下", "tv_wall": "后景", "center_floor": "中央"}
    valid, invalid = idx.validate_spatial_anchors("客厅", anchors)
    assert valid == ["sofa_L", "tv_wall", "center_floor"]
    assert invalid == []


def test_validate_spatial_anchors_some_invalid(tmp_project, sample_scene_layout):
    idx = AssetIndex(tmp_project)
    idx.add_scene_layout("客厅", sample_scene_layout)

    anchors = {"sofa_L": "画面左下", "fake_object": "不存在", "tv_wall": "后景"}
    valid, invalid = idx.validate_spatial_anchors("客厅", anchors)
    assert set(valid) == {"sofa_L", "tv_wall"}
    assert invalid == ["fake_object"]


def test_validate_spatial_anchors_no_layout(tmp_project):
    idx = AssetIndex(tmp_project)
    valid, invalid = idx.validate_spatial_anchors("客厅", {"any_key": "desc"})
    assert valid == []
    assert invalid == ["any_key"]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend && .venv/Scripts/python -m pytest tests/test_asset_index.py::test_validate_spatial_anchors_all_valid -v`
Expected: FAIL with `AttributeError: 'AssetIndex' object has no attribute 'validate_spatial_anchors'`

- [ ] **Step 3: Implement validate_spatial_anchors**

Add after `get_fixed_object_ids`:
```python
    def validate_spatial_anchors(self, scene_name: str, anchors: dict) -> tuple[list[str], list[str]]:
        """校验 spatial_anchors 键是否都在该场景的 layout 内。

        Returns:
            (valid_keys, invalid_keys) — 拆分两个列表便于报告
        """
        valid_ids = set(self.get_fixed_object_ids(scene_name))
        valid, invalid = [], []
        for key in anchors:
            (valid if key in valid_ids else invalid).append(key)
        return valid, invalid
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd backend && .venv/Scripts/python -m pytest tests/test_asset_index.py -v`
Expected: PASS for all 9 tests

- [ ] **Step 5: Commit**

```bash
git add backend/app/utils/asset_index.py backend/tests/test_asset_index.py
git commit -m "feat(asset_index): add validate_spatial_anchors"
```

---

## Task 5: AssetIndex — extend add_scene_master to accept layout

**Files:**
- Modify: `backend/app/utils/asset_index.py:83-96`
- Test: `backend/tests/test_asset_index.py`

- [ ] **Step 1: Write failing test**

Append to `backend/tests/test_asset_index.py`:
```python
def test_add_scene_master_with_layout(tmp_project, sample_scene_layout):
    idx = AssetIndex(tmp_project)
    idx.add_scene_master("客厅", tos_url="https://tos.example/x.png",
                         local_path="素材/场景/客厅_master.png",
                         prompt="客厅全景 prompt", layout=sample_scene_layout)

    assert idx.get_scene_master_url("客厅") == "https://tos.example/x.png"
    assert idx.get_scene_layout("客厅") == sample_scene_layout


def test_add_scene_master_without_layout_keeps_none(tmp_project):
    idx = AssetIndex(tmp_project)
    idx.add_scene_master("客厅", tos_url="https://tos.example/x.png")

    assert idx.get_scene_layout("客厅") is None
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend && .venv/Scripts/python -m pytest tests/test_asset_index.py::test_add_scene_master_with_layout -v`
Expected: FAIL with `TypeError: add_scene_master() got an unexpected keyword argument 'layout'`

- [ ] **Step 3: Modify add_scene_master to accept layout parameter**

Replace `add_scene_master` method (lines 83-96):
```python
    def add_scene_master(self, name: str, tos_url: str, local_path: str = "",
                         prompt: str = "", layout: Optional[dict] = None) -> str:
        """添加场景全景参考图。已存在则替换。
        若提供 layout，则一次性写入 master + spatial_layout。
        """
        data = self._read()
        scenes = data.setdefault("scenes", {})
        scene_entry = scenes.setdefault(name, {"master": None, "shot_frames": []})
        scene_entry["master"] = {
            "tos_url": tos_url,
            "local_path": local_path,
            "prompt": prompt,
            "created_at": datetime.now().isoformat(),
        }
        if layout is not None:
            scene_entry["spatial_layout"] = layout
        self._write(data)
        return f"{name}/master"
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd backend && .venv/Scripts/python -m pytest tests/test_asset_index.py -v`
Expected: PASS for all 11 tests

- [ ] **Step 5: Commit**

```bash
git add backend/app/utils/asset_index.py backend/tests/test_asset_index.py
git commit -m "feat(asset_index): add_scene_master accepts optional layout"
```

---

## Task 6: AssetIndex — add_shot_frame with fixed_objects

**Files:**
- Modify: `backend/app/utils/asset_index.py:107-127`
- Test: `backend/tests/test_asset_index.py`

- [ ] **Step 1: Write failing test**

Append to `backend/tests/test_asset_index.py`:
```python
def test_add_shot_frame_with_fixed_objects(tmp_project):
    idx = AssetIndex(tmp_project)
    idx.add_shot_frame("客厅", "客厅_master", "establishing",
                       tos_url="https://tos.example/f.png",
                       fixed_objects=["sofa_L", "tv_wall"])

    frame = idx.get_shot_frame("客厅", "客厅_master")
    assert frame["fixed_objects"] == ["sofa_L", "tv_wall"]


def test_add_shot_frame_default_empty_fixed_objects(tmp_project):
    idx = AssetIndex(tmp_project)
    idx.add_shot_frame("客厅", "客厅_master", "establishing",
                       tos_url="https://tos.example/f.png")

    frame = idx.get_shot_frame("客厅", "客厅_master")
    assert frame["fixed_objects"] == []
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend && .venv/Scripts/python -m pytest tests/test_asset_index.py::test_add_shot_frame_with_fixed_objects -v`
Expected: FAIL with `TypeError: add_shot_frame() got an unexpected keyword argument 'fixed_objects'`

- [ ] **Step 3: Modify add_shot_frame to accept fixed_objects parameter**

Replace `add_shot_frame` method (lines 107-127):
```python
    def add_shot_frame(self, scene_name: str, frame_id: str, frame_type: str,
                       tos_url: str, local_path: str = "", prompt: str = "",
                       fixed_objects: Optional[list[str]] = None) -> str:
        """添加场景取景框。frame_id 如 'coffee_bar_2shot'，parent 固定为 scene master。

        fixed_objects: 该取景框中可见的固定物 id 列表（来自 scene.spatial_layout.fixed_objects[].id）。
        """
        data = self._read()
        scenes = data.setdefault("scenes", {})
        scene_entry = scenes.setdefault(scene_name, {"master": None, "shot_frames": []})

        scene_entry["shot_frames"] = [
            f for f in scene_entry["shot_frames"] if f.get("frame_id") != frame_id
        ]
        scene_entry["shot_frames"].append({
            "frame_id": frame_id,
            "frame_type": frame_type,
            "tos_url": tos_url,
            "local_path": local_path,
            "prompt": prompt,
            "fixed_objects": fixed_objects or [],
            "created_at": datetime.now().isoformat(),
        })
        self._write(data)
        return f"{scene_name}/{frame_id}"
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd backend && .venv/Scripts/python -m pytest tests/test_asset_index.py -v`
Expected: PASS for all 13 tests

- [ ] **Step 5: Commit**

```bash
git add backend/app/utils/asset_index.py backend/tests/test_asset_index.py
git commit -m "feat(asset_index): add_shot_frame accepts fixed_objects"
```

---

## Task 7: Create layout_checker module

**Files:**
- Create: `backend/app/utils/layout_checker.py`
- Test: `backend/tests/test_layout_checker.py`

- [ ] **Step 1: Write failing test**

Create `backend/tests/test_layout_checker.py`:
```python
import pytest
from app.utils.layout_checker import (
    check_anchor_validity,
    check_cross_shot_continuity,
    format_report_markdown,
)


SAMPLE_LAYOUT = {
    "view": "front_elev",
    "fixed_objects": [
        {"id": "sofa_L", "name": "L型沙发", "position": "画面左下区域"},
        {"id": "tv_wall", "name": "电视墙", "position": "画面后景中央"},
        {"id": "window_R", "name": "落地窗", "position": "画面右侧通顶"},
    ],
    "walkable_zones": [
        {"id": "center_floor", "position": "画面中央中景"}
    ]
}


def test_check_anchor_validity_all_in_layout():
    anchors = {"sofa_L": "画面左下", "center_floor": "中央"}
    issues = check_anchor_validity(anchors, SAMPLE_LAYOUT)
    assert issues == []


def test_check_anchor_validity_finds_invalid_key():
    anchors = {"sofa_L": "画面左下", "fake_door": "右侧"}
    issues = check_anchor_validity(anchors, SAMPLE_LAYOUT)
    assert len(issues) == 1
    assert issues[0]["key"] == "fake_door"
    assert issues[0]["severity"] == "blocking"


def test_check_cross_shot_continuity_same_position():
    """同场景连续镜头，固定物位置应一致。"""
    shots = [
        {"shot_id": "S1_F01", "spatial_anchors": {"sofa_L": "画面左下", "tv_wall": "后景中央"}},
        {"shot_id": "S1_F02", "spatial_anchors": {"sofa_L": "画面左下", "tv_wall": "后景中央"}},
    ]
    issues = check_cross_shot_continuity(shots, SAMPLE_LAYOUT)
    assert issues == []


def test_check_cross_shot_continuity_object_disappears():
    """同场景下一镜某固定物消失 → blocking。"""
    shots = [
        {"shot_id": "S1_F01", "spatial_anchors": {"sofa_L": "画面左下", "tv_wall": "后景中央"}},
        {"shot_id": "S1_F02", "spatial_anchors": {"sofa_L": "画面左下"}},
    ]
    issues = check_cross_shot_continuity(shots, SAMPLE_LAYOUT)
    assert any(i["type"] == "object_disappeared" for i in issues)
    assert any(i["severity"] == "warning" for i in issues)


def test_check_cross_shot_continuity_object_appears():
    """同场景下一镜出现新固定物 → blocking（应从 layout 派生，不是凭空出现）。"""
    shots = [
        {"shot_id": "S1_F01", "spatial_anchors": {"sofa_L": "画面左下"}},
        {"shot_id": "S1_F02", "spatial_anchors": {"sofa_L": "画面左下", "tv_wall": "后景中央"}},
    ]
    issues = check_cross_shot_continuity(shots, SAMPLE_LAYOUT)
    assert any(i["type"] == "object_appeared" for i in issues)


def test_format_report_markdown_empty():
    out = format_report_markdown([])
    assert "无问题" in out or "通过" in out


def test_format_report_markdown_with_issues():
    issues = [
        {"shot_id": "S1_F02", "type": "invalid_key", "key": "fake",
         "severity": "blocking", "message": "fake 不在 layout 中"}
    ]
    out = format_report_markdown(issues)
    assert "S1_F02" in out
    assert "blocking" in out
    assert "fake" in out
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend && .venv/Scripts/python -m pytest tests/test_layout_checker.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'app.utils.layout_checker'`

- [ ] **Step 3: Implement layout_checker module**

Create `backend/app/utils/layout_checker.py`:
```python
"""跨镜头位置连续性校验。

检查两类问题：
1. invalid_key: spatial_anchors 键不在 scene.spatial_layout 内
2. object_appeared / object_disappeared: 同场景连续镜头中固定物出现/消失
"""

from typing import Optional


def _layout_id_set(layout: dict) -> set[str]:
    """从 layout 提取所有有效 id（含 fixed_objects 和 walkable_zones）。"""
    ids = {obj["id"] for obj in layout.get("fixed_objects", []) if "id" in obj}
    ids.update({z["id"] for z in layout.get("walkable_zones", []) if "id" in z})
    return ids


def check_anchor_validity(anchors: dict, layout: dict) -> list[dict]:
    """检查单个镜头的 spatial_anchors 是否全部来自 layout。"""
    valid_ids = _layout_id_set(layout)
    issues = []
    for key in anchors:
        if key not in valid_ids:
            issues.append({
                "type": "invalid_key",
                "key": key,
                "severity": "blocking",
                "message": f"空间锚点 '{key}' 不在 scene.spatial_layout 的 fixed_objects/walkable_zones 中"
            })
    return issues


def check_cross_shot_continuity(shots: list[dict], layout: dict) -> list[dict]:
    """检查同场景连续镜头的固定物连续性。

    shots: 同一场景的镜头列表（按 shot_id 顺序）
    """
    issues = []
    if len(shots) < 2:
        return issues

    for i in range(1, len(shots)):
        prev = shots[i - 1]
        curr = shots[i]
        prev_anchors = set(prev.get("spatial_anchors", {}).keys())
        curr_anchors = set(curr.get("spatial_anchors", {}).keys())

        disappeared = prev_anchors - curr_anchors
        appeared = curr_anchors - prev_anchors

        for key in disappeared:
            issues.append({
                "shot_id": curr.get("shot_id"),
                "type": "object_disappeared",
                "key": key,
                "severity": "warning",
                "message": f"固定物 '{key}' 在 {prev.get('shot_id')} 出现，{curr.get('shot_id')} 消失。请确认是否合理（摄影机切角度时可不出现）"
            })

        for key in appeared:
            issues.append({
                "shot_id": curr.get("shot_id"),
                "type": "object_appeared",
                "key": key,
                "severity": "blocking",
                "message": f"固定物 '{key}' 在 {prev.get('shot_id')} 未出现，{curr.get('shot_id')} 凭空出现。必须从 layout 派生，不允许凭空"
            })

    return issues


def check_episode(shots_by_scene: dict, layouts: dict) -> list[dict]:
    """校验整集。

    shots_by_scene: {scene_name: [shot_dict, ...]}
    layouts: {scene_name: layout_dict}
    """
    all_issues = []
    for scene_name, shots in shots_by_scene.items():
        layout = layouts.get(scene_name)
        if not layout:
            all_issues.append({
                "scene": scene_name,
                "type": "missing_layout",
                "severity": "blocking",
                "message": f"场景 '{scene_name}' 没有 spatial_layout，无法校验"
            })
            continue

        for shot in shots:
            anchors = shot.get("spatial_anchors", {})
            all_issues.extend(check_anchor_validity(anchors, layout))

        all_issues.extend(check_cross_shot_continuity(shots, layout))

    return all_issues


def format_report_markdown(issues: list[dict]) -> str:
    if not issues:
        return "# 站位校验报告\n\n✓ 全部通过，无问题\n"

    blocking = [i for i in issues if i.get("severity") == "blocking"]
    warnings = [i for i in issues if i.get("severity") == "warning"]

    lines = ["# 站位校验报告", ""]
    lines.append(f"共 {len(issues)} 处问题（{len(blocking)} blocking / {len(warnings)} warning）")
    lines.append("")

    if blocking:
        lines.append(f"## Blocking ({len(blocking)})")
        lines.append("")
        for i in blocking:
            shot = i.get("shot_id", i.get("scene", "?"))
            lines.append(f"- **{shot}** [{i['type']}] {i['message']}")
        lines.append("")

    if warnings:
        lines.append(f"## Warning ({len(warnings)})")
        lines.append("")
        for i in warnings:
            shot = i.get("shot_id", i.get("scene", "?"))
            lines.append(f"- **{shot}** [{i['type']}] {i['message']}")
        lines.append("")

    return "\n".join(lines)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd backend && .venv/Scripts/python -m pytest tests/test_layout_checker.py -v`
Expected: PASS for all 7 tests

- [ ] **Step 5: Commit**

```bash
git add backend/app/utils/layout_checker.py backend/tests/test_layout_checker.py
git commit -m "feat: add layout_checker module for cross-shot continuity validation"
```

---

## Task 8: CLI — extend scene-master with --layout

**Files:**
- Modify: `backend/app/cli.py:131-152`
- Test: manual verification (no test harness for argparse yet)

- [ ] **Step 1: Modify cmd_scene_master to accept --layout**

Replace `cmd_scene_master` in `backend/app/cli.py` (lines 131-152):
```python
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
```

- [ ] **Step 2: Add --layout argument to scene-master subparser**

Find the `scene-master` subparser (around line 367 in `backend/app/cli.py`) and replace:
```python
    p = sub.add_parser("scene-master", help="Generate scene panoramic master")
    p.add_argument("--project", required=True)
    p.add_argument("--name", required=True, help="Scene name")
    p.add_argument("--prompt", required=True, help="Image prompt (use '-' for stdin, '@file' for file)")
    p.add_argument("--ratio", default="9:16", help="Aspect ratio (default: 9:16)")
    p.add_argument("--layout", default=None, help="Scene spatial layout JSON (inline or '@file.json')")
```

- [ ] **Step 3: Verify CLI accepts the new flag**

Run: `cd backend && .venv/Scripts/python -m app.cli scene-master --help`
Expected: output shows `--layout LAYOUT` in the help

- [ ] **Step 4: Commit**

```bash
git add backend/app/cli.py
git commit -m "feat(cli): scene-master accepts --layout parameter"
```

---

## Task 9: CLI — extend shot-frame with --fixed-objects

**Files:**
- Modify: `backend/app/cli.py:155-179`
- Test: manual verification

- [ ] **Step 1: Modify cmd_shot_frame to accept --fixed-objects**

Replace `cmd_shot_frame` in `backend/app/cli.py` (lines 155-179):
```python
async def cmd_shot_frame(args):
    project_root = resolve_project(args.project)
    prompt = read_prompt(args.prompt)
    index = AssetIndex(project_root)

    if index.has_shot_frame(args.scene, args.frame_id):
        print(f"⊙ {args.scene}/{args.frame_id} 取景框已存在，跳过")
        return

    master = index.get_scene_master(args.scene)
    refs = [master["tos_url"]] if master and master.get("tos_url") else None

    fixed_objects = None
    if args.fixed_objects:
        fixed_objects = [s.strip() for s in args.fixed_objects.split(",") if s.strip()]

    logger.info("Shot frame: %s / %s (%s) fixed=%s", args.scene, args.frame_id, args.frame_type, fixed_objects)
    image_url, tos_url, img_bytes = await gen_and_upload(prompt, args.ratio, refs)

    local_dir = Path(project_root) / "素材" / "场景"
    local_dir.mkdir(parents=True, exist_ok=True)
    local_path = str(local_dir / f"{args.scene}_{args.frame_id}.png")
    if img_bytes:
        with open(local_path, "wb") as f:
            f.write(img_bytes)

    index.add_shot_frame(args.scene, args.frame_id, args.frame_type,
                         tos_url=tos_url, local_path=local_path,
                         prompt=prompt, fixed_objects=fixed_objects)
    if fixed_objects:
        print(f"✓ {args.scene}/{args.frame_id} ({len(fixed_objects)} 固定物) → {tos_url}")
    else:
        print(f"✓ {args.scene}/{args.frame_id} → {tos_url}")
```

- [ ] **Step 2: Add --fixed-objects argument**

Find the `shot-frame` subparser in `backend/app/cli.py` and replace:
```python
    p = sub.add_parser("shot-frame", help="Generate scene shot frame")
    p.add_argument("--project", required=True)
    p.add_argument("--scene", required=True, help="Scene name")
    p.add_argument("--frame-id", required=True, help="Frame identifier")
    p.add_argument("--frame-type", required=True, help="Frame type (e.g. two_shot, establishing)")
    p.add_argument("--prompt", required=True, help="Image prompt (use '-' for stdin, '@file' for file)")
    p.add_argument("--ratio", default="9:16", help="Aspect ratio (default: 9:16)")
    p.add_argument("--fixed-objects", default=None, help="Comma-separated fixed object ids from scene.spatial_layout")
```

- [ ] **Step 3: Verify CLI accepts the new flag**

Run: `cd backend && .venv/Scripts/python -m app.cli shot-frame --help`
Expected: output shows `--fixed-objects FIXED_OBJECTS` in the help

- [ ] **Step 4: Commit**

```bash
git add backend/app/cli.py
git commit -m "feat(cli): shot-frame accepts --fixed-objects parameter"
```

---

## Task 10: CLI — add layout-check subcommand

**Files:**
- Modify: `backend/app/cli.py`
- Test: manual integration test

- [ ] **Step 1: Add cmd_layout_check function**

Add new function to `backend/app/cli.py` (place before the `# ── Main ──` section):
```python
async def cmd_layout_check(args):
    """校验指定剧集的所有镜头的 spatial_anchors 连续性。"""
    from app.utils.layout_checker import check_episode, format_report_markdown

    project_root = resolve_project(args.project)
    index = AssetIndex(project_root)

    prompt_file = Path(project_root) / "提示词" / f"第{args.episode}集-视频提示词.json"
    if not prompt_file.exists():
        sys.exit(f"Video prompt JSON not found: {prompt_file}")

    data = json.loads(prompt_file.read_text(encoding="utf-8"))
    shots = data.get("shots", [])

    # Group shots by scene
    shots_by_scene = {}
    for shot in shots:
        scene = shot.get("scene_reference", {}).get("scene_name", "unknown")
        shots_by_scene.setdefault(scene, []).append(shot)

    # Collect layouts
    layouts = {}
    missing_layouts = []
    for scene_name in shots_by_scene:
        layout = index.get_scene_layout(scene_name)
        if layout:
            layouts[scene_name] = layout
        else:
            missing_layouts.append(scene_name)

    if missing_layouts and not args.skip_missing:
        print(f"Error: 以下场景缺失 spatial_layout: {missing_layouts}", file=sys.stderr)
        print("请先在 scene-card.md 中填写固定物空间布局，再调用 scene-master --layout 生成", file=sys.stderr)
        sys.exit(1)

    issues = check_episode(shots_by_scene, layouts)
    report = format_report_markdown(issues)

    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(report, encoding="utf-8")
        print(f"✓ 校验报告写入 {out_path}")
    else:
        print(report)

    blocking = [i for i in issues if i.get("severity") == "blocking"]
    sys.exit(2 if blocking else 0)
```

- [ ] **Step 2: Add layout-check subparser**

In the `main()` function, add before `video-prompt` subparser:
```python
    p = sub.add_parser("layout-check", help="Validate spatial_anchors continuity across shots")
    p.add_argument("--project", required=True, help="Project directory path")
    p.add_argument("--episode", required=True, help="Episode ID (e.g. 0001)")
    p.add_argument("--output", default=None, help="Output file path (default: stdout)")
    p.add_argument("--skip-missing", action="store_true", help="Skip scenes with missing spatial_layout")
```

- [ ] **Step 3: Add to sync_cmds set so it runs without asyncio**

In `main()`, find the line `sync_cmds = {"assets", "video-prompt"}` and update:
```python
    sync_cmds = {"assets", "video-prompt", "layout-check"}
```

- [ ] **Step 4: Verify CLI accepts the new command**

Run: `cd backend && .venv/Scripts/python -m app.cli layout-check --help`
Expected: output shows the help with --project, --episode, --output, --skip-missing

- [ ] **Step 5: End-to-end integration test**

Create a temp project for testing:
```bash
cd backend && .venv/Scripts/python -c "
import sys
sys.path.insert(0, '.')
from app.utils.asset_index import AssetIndex
import json, tempfile, os
with tempfile.TemporaryDirectory() as tmp:
    idx = AssetIndex(tmp)
    layout = {
      'view': 'front_elev',
      'fixed_objects': [
        {'id': 'sofa_L', 'name': 'L型沙发', 'position': '画面左下'},
        {'id': 'tv_wall', 'name': '电视墙', 'position': '后景中央'}
      ],
      'walkable_zones': []
    }
    idx.add_scene_layout('客厅', layout)
    # Write a fake video prompt JSON
    os.makedirs(os.path.join(tmp, '提示词'), exist_ok=True)
    prompt_data = {
      'shots': [
        {'shot_id': 'S1_F01', 'scene_reference': {'scene_name': '客厅'},
         'spatial_anchors': {'sofa_L': '画面左下', 'fake_obj': '不在layout中'}},
        {'shot_id': 'S1_F02', 'scene_reference': {'scene_name': '客厅'},
         'spatial_anchors': {'sofa_L': '画面左下'}},
      ]
    }
    with open(os.path.join(tmp, '提示词', '第0001集-视频提示词.json'), 'w', encoding='utf-8') as f:
        json.dump(prompt_data, f, ensure_ascii=False)
    print(f'Test project: {tmp}')
"
```

Then run: `cd backend && .venv/Scripts/python -m app.cli layout-check --project <tmp> --episode 0001`
Expected: non-zero exit, output mentions invalid_key for `fake_obj` and object_disappeared for `tv_wall`.

- [ ] **Step 6: Commit**

```bash
git add backend/app/cli.py
git commit -m "feat(cli): add layout-check subcommand"
```

---

## Task 11: Plugin template — scene-card.md add spatial layout table

**Files:**
- Modify: `plugin/templates/scene-card.md`

- [ ] **Step 1: Read current scene-card.md and add new section**

Current file has a "道具清单" table around line 21-25. Add a new section after it (before "场景中的典型活动"):

Insert this new section in `plugin/templates/scene-card.md` between "道具清单" table and "## 场景中的典型活动":

```markdown
## 固定物空间布局（影响所有取景框 → 强制贯穿视频提示词）

| 固定物 ID | 名称 | 画面位置 | 大小 | 朝向 | 备注 |
|----------|------|---------|------|------|------|
| | | 前/左/右/中央/后景 + 区域 | 占画面比例 | 朝向描述 | |

**说明**：
- ID 用英文短码（下划线分隔），全剧统一。如 `sofa_L`、`window_R`、`tv_wall`
- 画面位置用结构化方向：前(后景)/左/右/中央/上(天花)/下(地面)
- 朝向：物体开口/正面/背面的指向。如沙发"开口朝右"、电视墙"正面朝镜头"
- 至少列出 3-5 个本场景的主要固定物
- 禁止写通用物件（"墙"、 "地"）作为固定物，只写可作为镜头参照的实体物体
- 写入 scene-master --layout 时，转换为如下 JSON：
```json
{
  "view": "front_elev",
  "fixed_objects": [
    {"id": "<ID>", "name": "<名称>", "position": "<位置>", "size": "<大小>", "orientation": "<朝向>"}
  ],
  "walkable_zones": [
    {"id": "<zone_id>", "position": "<位置>", "description": "<说明>"}
  ]
}
```
```

- [ ] **Step 2: Commit**

```bash
git add plugin/templates/scene-card.md
git commit -m "feat(template): add spatial layout table to scene-card"
```

---

## Task 12: Plugin template — episode-script.md remove ASCII layout

**Files:**
- Modify: `plugin/templates/episode-script.md`

- [ ] **Step 1: Remove ASCII 空间布局 section**

In `plugin/templates/episode-script.md`, delete the entire "### ASCII 空间布局" section (current lines 13-26). It contains the box-drawing characters and legend.

Replace the deleted section with a single reference line, placed in the same position (between "**取景框序列**" and "### 分镜流图"):

```markdown
**空间参照**：本场景的固定物布局见 `设定集/场景档案/{场景名}.md` 的「固定物空间布局」表。所有镜头的 spatial_anchors 键必须取自该表。
```

- [ ] **Step 2: Commit**

```bash
git add plugin/templates/episode-script.md
git commit -m "feat(template): replace ASCII layout with scene-card reference"
```

---

## Task 13: Plugin skill — drama-init add layout step

**Files:**
- Modify: `plugin/skills/drama-init/SKILL.md`

- [ ] **Step 1: Add layout step after scene cards**

In `plugin/skills/drama-init/SKILL.md` Step 6 (Generate Project Files), find where scene cards are listed (currently doesn't have one explicitly — scene-cards are generated per-scene in drama-plan). Add a new step 6.5 after the existing step 6:

```markdown
### Step 6.5: Scene Spatial Layout Pre-fill

For each scene card generated in Step 6, fill the "固定物空间布局" table based on:
- Scene name and type (室内/室外/半开放)
- 关键地标 from scene card
- Typical use of the space (sitting room → sofa + TV + window, etc.)

**Do not** read the scene master image — derive layout from scene description only. The layout will be encoded into the scene-master prompt and used as the canonical spatial reference for all shot prompts.

Output: append a `## 固定物空间布局` section to each scene card in `设定集/场景档案/`.
```

- [ ] **Step 2: Commit**

```bash
git add plugin/skills/drama-init/SKILL.md
git commit -m "feat(skill): drama-init pre-fills scene spatial layout"
```

---

## Task 14: Plugin skill — drama-generate update prompt templates

**Files:**
- Modify: `plugin/skills/drama-generate/SKILL.md`

- [ ] **Step 1: Update scene-master prompt template**

In `plugin/skills/drama-generate/SKILL.md`, find the "## 阶段2：场景全景图" section. Replace the current prompt template:

```markdown
读取 `设定集/场景档案/`，对每个场景先取出"固定物空间布局"表，将其转换为 JSON，作为 `--layout` 参数传入。

**提示词模板**（用结构化空间描述）：

```
{场景类型}，{关键地标}，{空间尺寸}。

固定物空间布局（按结构化方向）：
- 前（后景）：{从 scene-card 复制}
- 左：{从 scene-card 复制}
- 右：{从 scene-card 复制}
- 中央：{从 scene-card 复制}
- 地面/天花：{可选}

{氛围基调}，{色调/光照方向}。空镜，无人物。
竖屏9:16构图，展示场景全貌。
```

调用（逐个场景执行）：

1. **先生成 layout JSON**（从 scene-card 表格）：

```bash
CLI scene-master --project <项目> --name <场景名> --prompt @<prompt_file> --layout @<layout_json_file>
```

CLI 内部把 layout 写入 `.drama/assets.json` 的 `spatial_layout` 字段。
```

- [ ] **Step 2: Update shot-frame template**

In `plugin/skills/drama-generate/SKILL.md` "## 阶段3a. 缺失取景框" section, add `--fixed-objects` to the example:

```markdown
drama-write 的分镜流图指定了每个镜头使用的取景框。Claude 提取去重后的取景框清单，逐个检查 `assets.json`，缺失的调用：

```bash
CLI shot-frame --project <项目目录> --scene <场景名> --frame-id <frame_id> --frame-type <type> --fixed-objects "<id1>,<id2>,..." --prompt "..."
```

`--fixed-objects` 列出该取景框中可见的固定物 id（从 scene.spatial_layout 中筛选）。
```

- [ ] **Step 3: Commit**

```bash
git add plugin/skills/drama-generate/SKILL.md
git commit -m "feat(skill): drama-generate uses structured spatial layout prompts"
```

---

## Task 15: Plugin reference — video-prompt-rules add §3.2 source constraint

**Files:**
- Modify: `plugin/references/video-prompt-rules.md`

- [ ] **Step 1: Append §3.2 after §3.1**

In `plugin/references/video-prompt-rules.md`, find the end of §3.1 (the cross-shot consistency checklist) and append:

```markdown

#### 3.2 spatial_anchors 来源约束

> **核心规则**：所有 shot 的 `spatial_anchors` 键**必须**从 `scene.spatial_layout` 的 `fixed_objects[].id` 和 `walkable_zones[].id` 集合中选取。

**禁止**：
- 凭空发明 layout 中不存在的固定物（如 layout 没有"门"，prompt 不得写"门在左侧"）
- 引入 layout 中未定义的区域名称

**允许**：
- 同一 key 在不同镜头中的位置描述可派生（如 "sofa_L" 在 F01 是"画面左下"，在 F02 可写"沙发在画面左侧可见"）
- walkable_zone 用来标注人物可活动区域

**校验**：`python -m app.cli layout-check --project <项目> --episode N` 会扫描所有 shot 的 spatial_anchors，自动检查违规键。Blocking 级错误会阻止生成。

**修复流程**：发现 invalid_key → 在 scene-card 中补上对应固定物 → 重新生成 master（如有结构变化）→ 更新所有 shot 的 spatial_anchors。
```

- [ ] **Step 2: Commit**

```bash
git add plugin/references/video-prompt-rules.md
git commit -m "feat(rules): add §3.2 spatial_anchors source constraint"
```

---

## Task 16: End-to-end integration test

**Files:**
- Create: `backend/tests/test_integration_layout.py`

- [ ] **Step 1: Write integration test**

Create `backend/tests/test_integration_layout.py`:
```python
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
        text=True
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
        text=True
    )

    assert "通过" in result.stdout or "无问题" in result.stdout
    assert result.returncode == 0
```

- [ ] **Step 2: Run integration test**

Run: `cd backend && .venv/Scripts/python -m pytest tests/test_integration_layout.py -v`
Expected: PASS for both tests

- [ ] **Step 3: Commit**

```bash
git add backend/tests/test_integration_layout.py
git commit -m "test: add end-to-end integration test for layout-check workflow"
```

---

## Task 17: Sync plugin files to marketplace cache

**Files:**
- Copy: cache files to repo's `plugin/` directory

- [ ] **Step 1: Sync changed plugin files**

Run:
```bash
cp "C:/Users/Vei1/.claude/plugins/cache/short-drama-writer-marketplace/short-drama-writer/0.1.0/templates/scene-card.md" "d:/PersonalFiles/Project_Space/short-drama-writer/plugin/templates/scene-card.md"
cp "C:/Users/Vei1/.claude/plugins/cache/short-drama-writer-marketplace/short-drama-writer/0.1.0/templates/episode-script.md" "d:/PersonalFiles/Project_Space/short-drama-writer/plugin/templates/episode-script.md"
cp "C:/Users/Vei1/.claude/plugins/cache/short-drama-writer-marketplace/short-drama-writer/0.1.0/skills/drama-init/SKILL.md" "d:/PersonalFiles/Project_Space/short-drama-writer/plugin/skills/drama-init/SKILL.md"
cp "C:/Users/Vei1/.claude/plugins/cache/short-drama-writer-marketplace/short-drama-writer/0.1.0/skills/drama-generate/SKILL.md" "d:/PersonalFiles/Project_Space/short-drama-writer/plugin/skills/drama-generate/SKILL.md"
cp "C:/Users/Vei1/.claude/plugins/cache/short-drama-writer-marketplace/short-drama-writer/0.1.0/references/video-prompt-rules.md" "d:/PersonalFiles/Project_Space/short-drama-writer/plugin/references/video-prompt-rules.md"
```

- [ ] **Step 2: Verify diff is expected**

Run: `cd d:/PersonalFiles/Project_Space/short-drama-writer && git status`
Expected: shows modified files in `plugin/` (already committed individually in tasks 11-15, should show no uncommitted changes since we just sync)

- [ ] **Step 3: Commit if needed**

```bash
cd d:/PersonalFiles/Project_Space/short-drama-writer && git status
```

If uncommitted changes appear from sync drift:
```bash
git add plugin/
git commit -m "chore: sync plugin files from cache"
```

---

## Self-Review Checklist

After implementation:

1. **Spec coverage:**
   - Data structure: Tasks 2-6 ✓
   - CLI extensions: Tasks 8-10 ✓
   - scene-card template: Task 11 ✓
   - episode-script template: Task 12 ✓
   - drama-init skill: Task 13 ✓
   - drama-generate skill: Task 14 ✓
   - video-prompt-rules: Task 15 ✓
   - layout_checker module: Task 7 ✓
   - End-to-end test: Task 16 ✓

2. **Placeholder scan:** All code blocks have complete content, no TBDs.

3. **Type consistency:**
   - `add_scene_layout(scene_name, layout: dict)` used consistently
   - `get_fixed_object_ids(scene_name) -> list[str]` used consistently
   - `validate_spatial_anchors(scene_name, anchors: dict) -> tuple[list[str], list[str]]` used consistently
   - `check_episode(shots_by_scene, layouts) -> list[dict]` used consistently

4. **No spec gaps.**
